"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict


class ThriftModel(BaseModel):
    """Base class wrapping a thrift-generated object as typed data.

    Composition over inheritance: models hold a copy of the prototype
    fields, converting to/from thrift objects at the boundary.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    @classmethod
    def from_prototype(cls, prototype: object) -> Self:
        data = {k: v for k, v in vars(prototype).items() if v is not None}
        return cls.model_validate(data)
