"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

import json
import time

from yuuki_core.ttypes import MIDType, OpType

from ..data import GroupSecurity
from .registry import CommandContext, EventContext, registry

# Security switch codes, in OpType order (see GroupSecurity.configure).
SWITCH_CODES = {0, 1, 2, 3}


async def _group_of(ctx: CommandContext):
    """The group a command refers to, or None outside groups."""
    message = ctx.message
    if message.to_type != MIDType.GROUP or message.to is None:
        return None
    return await ctx.bot.client.get_group(message.to)


async def _assert_privilege(ctx: CommandContext, extend_admins: bool) -> bool:
    """Whether the sender may use privileged group commands."""
    group = await _group_of(ctx)
    if group is None:
        return False
    privilege = list(ctx.config.yuuki.admin) + [group.owner.mid]
    if extend_admins:
        privilege += ctx.data.group_data(str(group.id)).extend_admins
    sender = ctx.message.from_
    if sender not in privilege:
        return False
    return True


@registry.on(OpType.SEND_MESSAGE)
async def on_send_message(ctx: EventContext) -> None:
    """Remote shutdown handshake on our own outgoing messages."""
    from yuuki_core.ttypes import ContentType

    bot = ctx.bot
    message = ctx.operation.message
    if message is None or message.content_type != ContentType.NONE:
        return
    if message.text == "[Yuuki] Remote Shutdown":
        await bot.send_text(str(message.to), bot.get_text("common.exit"))
        await bot.shutdown()


@registry.command("Help", help_text="Show bot information")
async def help_command(ctx: CommandContext) -> None:
    await ctx.reply(
        ctx.get_text(
            "help.info",
            name=ctx.bot.name,
            version=ctx.bot.version,
            man_page=ctx.config.yuuki.man_page,
            privacy="OpenSource - Licensed under MPL 2.0",
            url=ctx.config.yuuki.project_url,
            copyright=ctx.config.yuuki.copyright,
        )
    )


@registry.command("Version", help_text="Show bot version")
async def version_command(ctx: CommandContext) -> None:
    await ctx.reply(ctx.bot.version)


@registry.command("UserID", help_text="Show your LINE user ID")
async def user_id_command(ctx: CommandContext) -> None:
    assert ctx.message.from_ is not None
    await ctx.reply(
        ctx.get_text("user_id.prefix") + ctx.message.from_
    )


@registry.command("GetAllHelper", help_text="Show all helper accounts")
async def get_all_helper_command(ctx: CommandContext) -> None:
    bot = ctx.bot
    if not await _assert_privilege(ctx, extend_admins=True):
        return
    for account in bot.helpers:
        await bot.send_user(ctx.bot.send_to(ctx.message), account)


@registry.command("Speed", help_text="Measure response speed")
async def speed_command(ctx: CommandContext) -> None:
    start = time.time()
    await ctx.reply(ctx.get_text("speed.testing"))
    await ctx.reply(ctx.get_text("speed.result", seconds=time.time() - start))


@registry.command("SecurityMode", help_text="Toggle global security service")
async def security_mode_command(ctx: CommandContext) -> None:
    bot = ctx.bot
    if ctx.message.from_ not in ctx.config.yuuki.admin:
        return
    if len(ctx.args) == 1 and ctx.args[0] in {"0", "1"}:
        bot.data.store.global_data.security_service = ctx.args[0] == "1"
        bot.data.save()
        await ctx.reply(ctx.get_text("common.okay"))
        return
    if ctx.args:
        await ctx.reply(ctx.get_text("hint.enable_disable"))
        return
    await ctx.reply(str(bot.data.store.global_data.security_service))


async def _config_security(ctx: CommandContext, codes: list[int]) -> None:
    group_id = ctx.message.to
    assert group_id is not None
    security = ctx.data.group_data(group_id).security
    if security is None:
        security = GroupSecurity()
        ctx.data.group_data(group_id).security = security
    if codes:
        security.configure(codes)
    else:
        security.switches = {op: False for op in security.switches}
    ctx.data.save()


@registry.command("Switch", help_text="Enable group security switches")
async def switch_command(ctx: CommandContext) -> None:
    bot = ctx.bot
    if not ctx.message.text:
        return
    if not bot.data.store.global_data.security_service:
        await ctx.reply(
            ctx.get_text("security.disabled", name=bot.name)
        )
        return
    if not await _assert_privilege(ctx, extend_admins=True):
        return
    codes = []
    unknown = []
    first = ctx.message.text.split(" ")[0]
    for index, code in enumerate([first, *ctx.args]):
        if index == 0:
            continue
        if code.isdigit() and int(code) in SWITCH_CODES:
            codes.append(int(code))
        else:
            unknown.append(code.strip())
    await _config_security(ctx, codes)
    if codes:
        await ctx.reply(ctx.get_text("common.okay"))
    else:
        await ctx.reply(ctx.get_text("common.not_found"))
    if unknown:
        await ctx.reply(
            ctx.get_text("warn.unknown_args")
            + "\n({})".format(", ".join(unknown))
        )


@registry.command("DisableAll", help_text="Disable group security switches")
async def disable_all_command(ctx: CommandContext) -> None:
    bot = ctx.bot
    if not bot.data.store.global_data.security_service:
        await ctx.reply(
            ctx.get_text("security.disabled", name=bot.name)
        )
        return
    if not await _assert_privilege(ctx, extend_admins=True):
        return
    await _config_security(ctx, [])
    await ctx.reply(ctx.get_text("common.okay"))


@registry.command("ExtAdmin", help_text="Manage extend administrators")
async def ext_admin_command(ctx: CommandContext) -> None:
    group = await _group_of(ctx)
    if group is None:
        return
    group_id = str(group.id)
    group_data = ctx.data.group_data(group_id)
    sender = ctx.message.from_
    assert sender is not None
    privilege = list(ctx.config.yuuki.admin) + [group.owner.mid]

    if len(ctx.args) == 2:
        action, mid = ctx.args
        if sender not in privilege:
            return
        if action == "add":
            if mid not in group.member_mids:
                await ctx.reply(
                    ctx.get_text("error.user_not_in_group")
                )
            elif mid in group_data.extend_admins:
                await ctx.reply(ctx.get_text("common.added"))
            elif ctx.data.in_blacklist(mid):
                await ctx.reply(
                    ctx.get_text("blacklist.in_database")
                )
            else:
                group_data.extend_admins.append(mid)
                ctx.data.save()
                await ctx.reply(ctx.get_text("common.okay"))
        elif action == "delete":
            if mid in group_data.extend_admins:
                group_data.extend_admins.remove(mid)
                ctx.data.save()
                await ctx.reply(ctx.get_text("common.okay"))
            else:
                await ctx.reply(ctx.get_text("common.not_found"))
        return

    if not group_data.extend_admins:
        await ctx.reply(ctx.get_text("common.not_found"))
        return
    listed = []
    status = ""
    for member in group.members:
        if member.mid in group_data.extend_admins:
            status += f"{member.display_name}\n"
            listed.append(member.mid)
    for mid in group_data.extend_admins:
        if mid not in listed:
            status += "{}: {}\n".format(ctx.get_text("common.unknown"), mid)
    await ctx.reply(status + ctx.get_text("ext_admin.list_title"))


@registry.command("Status", help_text="Show group security status")
async def status_command(ctx: CommandContext) -> None:
    bot = ctx.bot
    group = await _group_of(ctx)
    if group is None:
        return
    if not bot.data.store.global_data.security_service:
        status = ctx.get_text("security.disabled", name=bot.name)
    else:
        security = ctx.data.group_data(str(group.id)).security
        if security is None:
            status = ctx.get_text(
                "security.default_status", owner=group.owner.display_name
            )
        else:
            status = ctx.get_text(
                "security.listening",
                url=security.switches.get(11),  # NOTIFIED_UPDATE_GROUP
                invite=security.switches.get(13),  # NOTIFIED_INVITE_INTO_GROUP
                join=security.switches.get(17),  # NOTIFIED_ACCEPT_GROUP_INVITATION
                members=security.switches.get(19),  # NOTIFIED_KICKOUT_FROM_GROUP
                owner=group.owner.display_name,
            )
    await ctx.reply(status)


@registry.command("GroupBackup", help_text="Export the group member list")
async def group_backup_command(ctx: CommandContext) -> None:
    bot = ctx.bot
    group = await _group_of(ctx)
    if group is None:
        return
    if not await _assert_privilege(ctx, extend_admins=True):
        return
    layout = {
        "OriginID": group.id,
        "Members": group.member_mids,
        "Invites": group.invitee_mids or None,
    }
    sender = ctx.message.from_
    assert sender is not None
    await bot.send_text(sender, str(group.name))
    await bot.send_text(sender, json.dumps(layout))
    await ctx.reply(ctx.get_text("common.okay"))


@registry.command("Quit", help_text="Make the bot leave this group")
async def quit_command(ctx: CommandContext) -> None:
    group = await _group_of(ctx)
    if group is None:
        return
    if not await _assert_privilege(ctx, extend_admins=False):
        return
    await ctx.bot.leave_group(group)


@registry.command("Exit", help_text="Shut the bot down (admin only)")
async def exit_command(ctx: CommandContext) -> None:
    if ctx.message.from_ not in ctx.config.yuuki.admin:
        return
    await ctx.reply(ctx.get_text("common.exit"))
    await ctx.bot.shutdown()
