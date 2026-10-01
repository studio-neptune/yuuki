"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from yuuki_core import ttypes

from src.model import Group, Message, Operation, User


def test_operation_from_prototype():
    prototype = ttypes.Operation(
        revision=7,
        createdTime=123,
        type=26,
        reqSeq=1,
        param1="g1",
        param2="u1",
        param3="u2",
        message=ttypes.Message(from_="u1", to="g1", text="hello"),
    )
    operation = Operation.from_prototype(prototype)
    assert operation.revision == 7
    assert operation.op_type == 26
    assert operation.group_id == "g1"
    assert operation.actor == "u1"
    assert operation.target == "u2"
    assert operation.message is not None
    assert operation.message.text == "hello"


def test_message_roundtrip():
    message = Message.text_message("g1", "hi")
    prototype = message.to_prototype()
    assert prototype.to == "g1"
    assert prototype.text == "hi"
    rebuilt = Message.from_prototype(prototype)
    assert rebuilt == message


def test_group_members():
    prototype = ttypes.Group(
        id="g1",
        name="crew",
        members=[ttypes.Contact(mid="u1", displayName="A")],
        invitee=[ttypes.Contact(mid="u2")],
    )
    group = Group.from_prototype(prototype)
    assert group.member_mids == ["u1"]
    assert group.invitee_mids == ["u2"]
    assert group.owner.mid == "u1"


def test_group_owner_fallback():
    prototype = ttypes.Group(
        id="g1",
        members=[ttypes.Contact(mid="u1"), ttypes.Contact(mid="u2")],
    )
    group = Group.from_prototype(prototype)
    assert group.owner.mid == "u1"


def test_user_roundtrip():
    user = User.from_prototype(
        ttypes.Contact(mid="u1", displayName="A", pictureStatus="p")
    )
    assert user.display_name == "A"
    prototype = user.to_prototype()
    assert prototype.mid == "u1"
