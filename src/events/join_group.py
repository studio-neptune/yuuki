"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

from yuuki_core.ttypes import OpType

from ..model import Group
from .registry import EventContext, registry

LIST_SEPARATOR = "\x1e"


def _invited_accounts(ctx: EventContext, account: str) -> bool:
    """Whether this invite operation targets the given account."""
    target = ctx.operation.target
    if target is None:
        return False
    return account in target.split(LIST_SEPARATOR)


@registry.on(OpType.NOTIFIED_INVITE_INTO_GROUP)
async def on_invite_into_group(ctx: EventContext) -> None:
    """Accept or reject group invitations for all our accounts."""
    bot = ctx.bot
    operation = ctx.operation
    assert operation.group_id is not None
    actor = operation.actor
    assert actor is not None

    blocked = ctx.data.in_blacklist(actor)
    if _invited_accounts(ctx, bot.my_mid) and not blocked:
        group = await bot.client.get_group(operation.group_id)
        member_count = len(group.member_mids)
        await bot.client.accept_group_invitation(operation.group_id)
        if member_count >= ctx.config.yuuki.group_members_demand:
            await _accept(ctx, group, actor)
        else:
            await _reject(ctx, operation.group_id, actor)
    if not blocked and operation.group_id in ctx.data.store.global_data.group_joined:
        for account in bot.helpers:
            if _invited_accounts(ctx, account):
                await bot.helpers[account].accept_group_invitation(
                    operation.group_id
                )
                await bot.get_group_ticket(operation.group_id, account, renew=True)
                ctx.data.append_log(
                    "JoinGroup",
                    (ctx.data.now(), operation.group_id, account, actor),
                )


async def _accept(ctx: EventContext, group: Group, actor: str) -> None:
    bot = ctx.bot
    group_id = str(group.id)
    assert group_id == ctx.operation.group_id
    ctx.data.store.global_data.group_joined.append(group_id)
    ctx.data.save()
    await bot.send_text(
        group_id,
        bot.get_text("greeting", name=bot.name),
    )
    await bot.send_text(
        group_id,
        bot.get_text(
            "help.hint", name=bot.name, owner=group.owner.display_name
        ),
    )
    await bot.get_group_ticket(group_id, bot.my_mid, renew=True)
    ctx.data.append_log(
        "JoinGroup",
        (ctx.data.now(), group.name, group_id, actor),
    )


async def _reject(ctx: EventContext, group_id: str, actor: str) -> None:
    bot = ctx.bot
    demand = ctx.config.yuuki.group_members_demand
    await bot.send_text(
        group_id,
        bot.get_text("join.members_not_satisfied", demand=demand),
    )
    await bot.client.leave_group(group_id)
    ctx.data.append_log(
        "JoinGroup", (ctx.data.now(), group_id, "Not Join", actor)
    )
