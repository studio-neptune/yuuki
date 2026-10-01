"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

import logging

from yuuki_core.ttypes import OpType

from ..model import Group, Operation
from .registry import EventContext, registry

logger = logging.getLogger(__name__)

LIST_SEPARATOR = "\x1e"


def _security_enabled(ctx: EventContext, op_type: int, group_id: str) -> bool:
    """Whether the security service acts on this operation for this group."""
    if not ctx.data.store.global_data.security_service:
        return False
    security = ctx.data.group_data(group_id).security
    if security is None:
        return True
    return security.allows(op_type)


@registry.on(OpType.NOTIFIED_UPDATE_GROUP)
async def on_update_group(ctx: EventContext) -> None:
    """Someone opened the group join URL - close it and kick the actor."""
    bot = ctx.bot
    operation = ctx.operation
    assert operation.group_id is not None
    if not _security_enabled(ctx, operation.op_type, operation.group_id):
        return
    if operation.target != "4":  # 4 = group URL status change
        return
    group = await bot.client.get_group(operation.group_id)
    actor = operation.actor
    assert actor is not None
    if group.prevent_join_by_ticket or actor in bot.helpers:
        return
    if actor in await bot.group_privilege(group):
        return
    await bot.change_group_url_status(group, False)
    await bot.send_text(
        operation.group_id,
        ctx.get_text("warn.url_status"),
    )
    kicker = await bot.modify_group_member_list(1, group, actor)
    ctx.data.append_log(
        "KickEvent",
        (
            ctx.data.now(),
            group.name,
            operation.group_id,
            kicker,
            actor,
            operation.target,
            operation.op_type,
        ),
    )


@registry.on(OpType.NOTIFIED_INVITE_INTO_GROUP)
async def on_invite_into_group(ctx: EventContext) -> None:
    """Cancel invites of users outside the privileged circle."""
    bot = ctx.bot
    operation = ctx.operation
    assert operation.group_id is not None
    if not _security_enabled(ctx, operation.op_type, operation.group_id):
        return
    group = await bot.client.get_group(operation.group_id)
    target = operation.target
    assert target is not None
    privilege = await bot.group_privilege(group)
    allowed = bot.all_account_ids + privilege
    canceled_any = False
    for user in target.split(LIST_SEPARATOR):
        if user in allowed:
            continue
        if user in group.invitee_mids:
            handler = await bot.modify_group_member_list(2, group, user)
        else:
            handler = await bot.modify_group_member_list(1, group, user)
            ctx.data.append_log(
                "KickEvent",
                (
                    ctx.data.now(),
                    group.name,
                    operation.group_id,
                    handler,
                    operation.actor,
                    user,
                    operation.op_type * 10,
                ),
            )
        canceled_any = True
    ctx.data.append_log(
        "CancelEvent",
        (
            ctx.data.now(),
            group.name,
            operation.group_id,
            operation.actor,
            target.replace(LIST_SEPARATOR, ","),
        ),
    )
    if canceled_any:
        await bot.send_text(
            operation.group_id, ctx.get_text("warn.do_not_invite")
        )


@registry.on(OpType.NOTIFIED_ACCEPT_GROUP_INVITATION)
async def on_accept_group_invitation(ctx: EventContext) -> None:
    """A blacklisted user joined the group - kick them out."""
    bot = ctx.bot
    operation = ctx.operation
    assert operation.group_id is not None
    actor = operation.actor
    assert actor is not None
    if not ctx.data.in_blacklist(actor):
        return
    if not _security_enabled(ctx, operation.op_type, operation.group_id):
        return
    group = await bot.client.get_group(operation.group_id)
    if actor in await bot.group_privilege(group):
        return
    await bot.send_text(
        operation.group_id, ctx.get_text("blacklist.bye")
    )
    kicker = await bot.modify_group_member_list(1, group, actor)
    ctx.data.append_log(
        "KickEvent",
        (
            ctx.data.now(),
            group.name,
            operation.group_id,
            kicker,
            actor,
            actor,
            operation.op_type,
        ),
    )


@registry.on(OpType.NOTIFIED_KICKOUT_FROM_GROUP)
async def on_kickout_from_group(ctx: EventContext) -> None:
    """The core protection: rescue kicked accounts, punish the kicker."""
    bot = ctx.bot
    operation = ctx.operation
    assert operation.group_id is not None
    actor = operation.actor
    target = operation.target
    assert actor is not None and target is not None
    if not _security_enabled(ctx, operation.op_type, operation.group_id):
        return
    group = await bot.client.get_group(operation.group_id)
    if actor in await bot.group_privilege(group):
        return

    if actor in bot.helpers:
        # One of our helpers performed a kick (e.g. our own moderation).
        ctx.data.append_log(
            "KickEvent",
            (
                ctx.data.now(),
                group.name,
                operation.group_id,
                actor,
                actor,
                target,
                operation.op_type * 10 + 1,
            ),
        )
        return

    if target in bot.all_account_ids:
        await _rescue(ctx, group, operation)
        return

    await _kick_the_kicker(ctx, group, operation)


async def _kick_the_kicker(
    ctx: EventContext, group: Group, operation: Operation
) -> None:
    bot = ctx.bot
    actor = operation.actor
    target = operation.target
    assert actor is not None and target is not None
    await bot.send_text(
        str(group.id), ctx.get_text("warn.do_not_kick")
    )
    kicker = await bot.modify_group_member_list(1, group, actor)
    ctx.data.append_log(
        "KickEvent",
        (
            ctx.data.now(),
            group.name,
            group.id,
            kicker,
            actor,
            target,
            operation.op_type,
        ),
    )
    await bot.send_text(
        str(group.id), ctx.get_text("kick.intro")
    )
    await bot.send_user(str(group.id), target)


async def _rescue(ctx: EventContext, group: Group, operation: Operation) -> None:
    """Re-invite a kicked account and blacklist the kicker."""
    bot = ctx.bot
    actor = operation.actor
    target = operation.target
    group_id = str(operation.group_id)
    assert actor is not None and target is not None

    if ctx.data.add_blacklist(actor):
        ctx.data.append_log(
            "BlackList", (ctx.data.now(), actor, group_id)
        )
        await bot.send_text(
            actor, ctx.get_text("blacklist.blocked")
        )

    try:
        kicker = await bot.modify_group_member_list(1, group, actor, target)
        await _reinvite(ctx, group, operation, kicker)
    except Exception:
        logger.exception("Rescue failed for %s", target)
        await _rescue_failure(ctx, group, operation)


async def _reinvite(
    ctx: EventContext,
    group: Group,
    operation: Operation,
    kicker: str,
    target_ticket_owner: str | None = None,
) -> None:
    """Bring the kicked account back via a group ticket."""
    bot = ctx.bot
    target = operation.target
    assert target is not None and operation.group_id is not None
    group_id = str(operation.group_id)
    url_was_closed = group.prevent_join_by_ticket
    if url_was_closed:
        await bot.change_group_url_status(group, True, kicker)
    ticket = await bot.get_group_ticket(group_id, kicker)
    try:
        await bot.client_for(target).accept_group_invitation_by_ticket(
            group_id, ticket
        )
    except Exception:
        if url_was_closed:
            await bot.change_group_url_status(group, True, kicker)
        ticket = await bot.get_group_ticket(group_id, kicker, renew=True)
        await bot.client_for(target).accept_group_invitation_by_ticket(
            group_id, ticket
        )
    if url_was_closed:
        await bot.change_group_url_status(group, False, target)
    await bot.get_group_ticket(group_id, target, renew=True)


async def _rescue_failure(
    ctx: EventContext, group: Group, operation: Operation
) -> None:
    bot = ctx.bot
    actor = operation.actor
    target = operation.target
    assert actor is not None and target is not None
    logger.error(
        "SecurityService failure: kicker=%s victim=%s group=%s",
        actor,
        target,
        operation.group_id,
    )
    if target == bot.my_mid:
        joined = ctx.data.store.global_data.group_joined
        if operation.group_id in joined:
            joined.remove(str(operation.group_id))
        ctx.data.save()
    ctx.data.append_log(
        "KickEvent",
        (
            ctx.data.now(),
            group.name,
            operation.group_id,
            "None",
            actor,
            target,
            operation.op_type * 10 + 3,
        ),
    )
