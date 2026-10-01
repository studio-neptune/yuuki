"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

import base64
import functools
import hashlib
import logging
import random
import re
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TYPE_CHECKING, cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..model import User

if TYPE_CHECKING:
    from ..bot import Yuuki

logger = logging.getLogger(__name__)

Handler = Callable[..., Awaitable[object]]

COOKIE_NAME = "yuuki_admin"
LOG_LINE = re.compile(r"<li>(.*?)</li>")

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"
LOG_DOCTYPES = ("JoinGroup", "KickEvent", "CancelEvent", "BlackList")


class WebAdmin:
    """FastAPI-based WebAdmin running inside the bot's event loop."""

    def __init__(self, bot: Yuuki, password: str | None = None) -> None:
        self.bot = bot
        self.password = password or str(hash(random.random()))
        self.sessions: set[str] = set()
        self.app = FastAPI(title="NepSecretary - Yuuki WebAdmin")
        self.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
        self.app.mount("/static", StaticFiles(directory=str(STATIC_DIR)))
        self._register_routes()

    # --- helpers ---

    def _media_url(self, picture_status: str | None) -> str | None:
        if picture_status is None:
            return None
        return f"{self.bot.media_server}/{picture_status}"

    def _profile_payload(self, profile: User) -> dict:
        return {
            "id": profile.mid,
            "version": self.bot.version,
            "name": profile.display_name,
            "status": profile.status_message,
            "picture": self._media_url(profile.picture_status),
        }

    async def _authorized(self, request: Request) -> bool:
        session = request.cookies.get(COOKIE_NAME)
        return session is not None and session in self.sessions

    def _unauthorized(self) -> JSONResponse:
        response = JSONResponse({"status": 403})
        response.set_cookie(COOKIE_NAME, "", expires=0)
        return response

    def _register_routes(self) -> None:
        app = self.app

        def require_auth(function: Handler) -> Handler:
            @functools.wraps(function)
            async def guarded(*args: object, **kwargs: object) -> object:
                request = kwargs.get("request")
                if request is None:
                    assert args, "handler requires a Request"
                    request = args[0]
                if not await self._authorized(cast("Request", request)):
                    return self._unauthorized()
                return await function(*args, **kwargs)

            return guarded

        @app.get("/")
        async def index(request: Request):
            return self.templates.TemplateResponse(
                request,
                "index.html",
                {
                    "name": self.bot.name,
                    "authorized": await self._authorized(request),
                },
            )

        @app.get("/logout")
        async def logout(request: Request):
            session = request.cookies.get(COOKIE_NAME)
            if session is not None:
                self.sessions.discard(session)
            response = RedirectResponse("/", status_code=302)
            response.set_cookie(COOKIE_NAME, "", expires=0)
            return response

        @app.get("/logo")
        async def logo():
            """The logo as a plain data-URI or URL, used as an img src."""
            logo_path = Path(__file__).parents[2] / "logo.png"
            if logo_path.is_file():
                data = base64.b64encode(logo_path.read_bytes()).decode("utf8")
                return PlainTextResponse(f"data:image/png;base64, {data}")
            return PlainTextResponse(
                "https://raw.githubusercontent.com/studio-neptune/"
                "yuuki/main/logo.png"
            )

        @app.post("/api/verify")
        async def verify(request: Request):
            form = await request.form()
            code = form.get("code")
            if code == self.password:
                seed = str(hash(random.random() + time.time())).encode("utf-8")
                session_key = hashlib.sha256(seed).hexdigest()
                self.sessions.add(session_key)
                response = JSONResponse(
                    {"status": 200, "session": session_key}
                )
                response.set_cookie(COOKIE_NAME, session_key)
                return response
            return JSONResponse({"status": 401})

        @app.get("/api/profile")
        @require_auth
        async def profile(request: Request):
            assert self.bot.profile is not None
            return self._profile_payload(self.bot.profile)

        @app.put("/api/profile")
        async def update_profile(request: Request):
            form = await request.form()
            name, status = form.get("name"), form.get("status")
            if name is None or status is None:
                return JSONResponse({"status": 400})
            from yuuki_core.ttypes import Profile

            await self.bot.client._call(  # noqa: SLF001
                "updateProfile", 0, Profile(displayName=name, statusMessage=status)
            )
            self.bot.profile = await self.bot.client.get_profile()
            return JSONResponse({"status": 200})

        @app.get("/api/groups")
        @require_auth
        async def groups(request: Request):
            return self.bot.data.store.global_data.group_joined

        @app.post("/api/groups")
        async def join_group(request: Request):
            form = await request.form()
            group_id = form.get("id")
            if group_id is None:
                return JSONResponse({"status": 400})
            await self.bot.client.accept_group_invitation(str(group_id))
            return JSONResponse({"status": 200})

        @app.delete("/api/groups")
        async def leave_group(request: Request):
            form = await request.form()
            group_id = form.get("id")
            if group_id is None:
                return JSONResponse({"status": 400})
            group = await self.bot.client.get_group(str(group_id))
            await self.bot.leave_group(group)
            return JSONResponse({"status": 200})

        @app.post("/api/group/ticket")
        async def group_ticket(request: Request):
            form = await request.form()
            group_id, ticket = form.get("id"), form.get("ticket")
            if group_id is None or ticket is None:
                return JSONResponse({"status": 400})
            await self.bot.client.accept_group_invitation_by_ticket(
                str(group_id), str(ticket)
            )
            return JSONResponse({"status": 200})

        @app.get("/api/groups/{group_ids}")
        @require_auth
        async def groups_information(request: Request, group_ids: str):
            ids = group_ids.split(",")
            groups = []
            for group in await self.bot.client.get_groups(ids):
                groups.append(
                    {
                        "id": group.id,
                        "name": group.name,
                        "picture": self._media_url(group.picture_status),
                        "members": [
                            self._profile_payload(member)
                            for member in group.members
                        ],
                        "invitee": [
                            self._profile_payload(contact)
                            for contact in group.invitee
                        ],
                        "creator": (
                            self._profile_payload(group.creator)
                            if group.creator is not None
                            else None
                        ),
                    }
                )
            return groups

        @app.get("/api/helpers")
        @require_auth
        async def helpers(request: Request):
            profiles = []
            for _account, helper in self.bot.helpers.items():
                profile = await helper.get_profile()
                profiles.append(self._profile_payload(profile))
            return profiles

        @app.get("/api/settings")
        @require_auth
        async def settings(request: Request):
            return {
                "security_service": (
                    self.bot.data.store.global_data.security_service
                ),
                "default_language": self.bot.config.yuuki.default_language,
                "hour_kick_limit": self.bot.config.yuuki.hour_kick_limit,
                "hour_cancel_limit": self.bot.config.yuuki.hour_cancel_limit,
                "group_members_demand": (
                    self.bot.config.yuuki.group_members_demand
                ),
            }

        @app.get("/api/events/{doctype}")
        @require_auth
        async def get_logs(request: Request, doctype: str):
            if doctype not in LOG_DOCTYPES:
                return JSONResponse({"status": 404})
            log_file = self.bot.data.log_path / (f"{doctype}.html")
            return LOG_LINE.findall(log_file.read_text(encoding="utf-8"))

        @app.post("/api/broadcast")
        async def broadcast(request: Request):
            form = await request.form()
            message, audience = form.get("message"), form.get("audience")
            if not message or audience != "groups":
                return JSONResponse({"status": 404})
            for group_id in self.bot.data.store.global_data.group_joined:
                await self.bot.send_text(group_id, str(message))
            return JSONResponse({"status": 200})

        @app.get("/api/shutdown")
        async def shutdown(request: Request):
            self.bot.power = False
            return JSONResponse({"status": 200})
