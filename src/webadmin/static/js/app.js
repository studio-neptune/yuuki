/*
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

/* Alpine.js frontend of the WebAdmin.
 * Hash-based views over the same /api endpoints as the v6 console. */

const EVENT_DOCTYPES = ["JoinGroup", "BlackList", "KickEvent", "CancelEvent"];

function hasSession() {
    return document.cookie.split(";").some(
        (entry) => entry.trim().startsWith("yuuki_admin=")
    );
}

async function fetchJson(url, options) {
    const response = await fetch(url, Object.assign(
        {credentials: "same-origin"}, options || {}
    ));
    return await response.json();
}

document.addEventListener("alpine:init", () => {
    Alpine.data("webadmin", () => ({
        // --- state ---
        authorized: false,
        view: "login",
        doctype: "",
        version: "",
        password: "",
        loginMessage: "",
        logo: "",
        profile: {id: "", name: "", status: "", picture: null},
        modify: false,
        groups: [{name: "Loading...", systemMessage: true}],
        helpers: [],
        events: [],
        eventPreviews: [],
        broadcastText: "",
        broadcastGroups: false,
        broadcastBusy: false,
        shutdownStatus: false,

        pages: [
            {path: "#/dashboard", view: "dashboard", title: "Dashboard"},
            {path: "#/groups", view: "groups", title: "Groups"},
            {path: "#/helpers", view: "helpers", title: "Helpers"},
            {path: "#/settings", view: "settings", title: "Settings"},
        ],

        settings: [],

        // --- lifecycle ---

        init() {
            this.settings = [
                {
                    title: "Profile",
                    color: "#007bff",
                    preview: "Edit LINE profile of the console BOT.",
                    action: () => this.go("#/profile"),
                },
                {
                    title: "Yuuki Configure",
                    color: "#e83e8c",
                    preview: "Settings for the BOT works.",
                    action: () => alert("Unavailable"),
                },
                {
                    title: "Shutdown",
                    color: "#6f42c1",
                    preview: "Turn off the BOT.",
                    action: () => this.shutdown(),
                },
            ];
            this.eventPreviews = [
                {doctype: "JoinGroup", title: "Join Event", color: "#6f42c1", preview: "Loading..."},
                {doctype: "BlackList", title: "Block Event", color: "#007bff", preview: "Loading..."},
                {doctype: "KickEvent", title: "Kick Event", color: "#e83e8c", preview: "Loading..."},
                {doctype: "CancelEvent", title: "Cancel Event", color: "#00ff00", preview: "Loading..."},
            ];
            window.addEventListener("hashchange", () => this.route());
            this.route();
        },

        // --- routing ---

        route() {
            this.authorized = hasSession();
            const path = location.hash || "#/";
            const known = [
                "#/", "#/dashboard", "#/groups", "#/helpers",
                "#/settings", "#/profile", "#/about",
            ];
            const eventsMatch = path.match(/^#\/events\/(\w+)$/);
            if (eventsMatch) {
                this.doctype = eventsMatch[1];
                this.setView("events");
                return;
            }
            if (!known.includes(path)) {
                this.setView("notfound");
                return;
            }
            if (!this.authorized && path !== "#/" && path !== "#/about") {
                location.hash = "#/";
                return;
            }
            const view = path === "#/" ? "login" : path.slice(2);
            this.setView(view);
        },

        setView(view) {
            this.view = view;
            if (!this.authorized && view !== "about" && view !== "login") {
                location.hash = "#/";
                return;
            }
            switch (view) {
                case "dashboard":
                    this.loadDashboard();
                    break;
                case "groups":
                    this.loadGroups();
                    break;
                case "helpers":
                    this.loadHelpers();
                    break;
                case "profile":
                    this.loadProfile();
                    break;
                case "events":
                    this.loadEvents(this.doctype);
                    break;
                case "about":
                    this.loadLogo();
                    break;
            }
        },

        go(hash) {
            location.hash = hash;
        },

        toggleAbout() {
            this.go(location.hash === "#/about" ? "#/" : "#/about");
        },

        // --- login ---

        async authorize() {
            const body = new FormData();
            body.append("code", this.password);
            const result = await fetchJson("/api/verify", {method: "POST", body});
            if (result.status === 200) {
                location.hash = "#/dashboard";
                location.reload();
            } else {
                this.loginMessage = "Wrong password";
            }
        },

        // --- dashboard ---

        async loadDashboard() {
            const profile = await fetchJson("/api/profile");
            this.version = profile.version;
            this.profile = profile;
            for (const event of this.eventPreviews) {
                const entries = await fetchJson(`/api/events/${event.doctype}`);
                event.preview = entries.length
                    ? entries[entries.length - 1]
                    : "(empty)";
            }
        },

        async broadcast() {
            if (!this.broadcastText) return alert("Empty message");
            if (!this.broadcastGroups) return alert("No audience selected");
            if (!confirm("The message will be broadcast, are you sure?")) return;
            this.broadcastBusy = true;
            const body = new FormData();
            body.set("message", this.broadcastText);
            body.set("audience", "groups");
            await fetchJson("/api/broadcast", {method: "POST", body});
            this.broadcastText = "";
            this.broadcastBusy = false;
        },

        // --- groups ---

        groupStatus(group) {
            const members = group.members ? group.members.length : 0;
            const invitee = group.invitee ? group.invitee.length : 0;
            return `Members:${members} Invites:${invitee}`;
        },

        async loadGroups() {
            const joined = await fetchJson("/api/groups");
            if (!joined.length) {
                this.groups = [{name: "(empty)", systemMessage: true}];
                return;
            }
            this.groups = await fetchJson(`/api/groups/${joined.join(",")}`);
        },

        async leaveGroup(groupId) {
            if (!confirm("The group will be removed from the BOT, are you sure?")) {
                return;
            }
            const body = new FormData();
            body.append("id", groupId);
            await fetchJson("/api/groups", {method: "DELETE", body});
            this.groups = this.groups.filter((group) => group.id !== groupId);
        },

        // --- helpers ---

        async loadHelpers() {
            const helpers = await fetchJson("/api/helpers");
            this.helpers = helpers.length ? helpers : [{name: "(empty)"}];
        },

        // --- profile ---

        async loadProfile() {
            this.profile = await fetchJson("/api/profile");
            this.modify = false;
        },

        async switchModify() {
            if (this.modify) {
                const body = new FormData();
                body.append("name", this.profile.name);
                body.append("status", this.profile.status);
                await fetchJson("/api/profile", {method: "PUT", body});
            }
            this.modify = !this.modify;
        },

        escapeHtml(text) {
            const map = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;",
            };
            return String(text).replace(/[&<>"']/g, (match) => map[match]);
        },

        get statusMessage() {
            return this.escapeHtml(this.profile.status).replace(/\n/g, "<br />");
        },

        // --- events ---

        async loadEvents(doctype) {
            const entries = await fetchJson(`/api/events/${doctype}`);
            if (entries.length) {
                this.events = entries.map((entry) => entry
                    ? {
                        title: entry.substring(0, 24),
                        content: entry.substring(26, entry.length),
                    }
                    : {title: "(unknown)", content: ""}
                );
            } else {
                this.events = [{title: "(empty)", content: ""}];
            }
        },

        // --- settings ---

        async shutdown() {
            this.shutdownStatus = true;
            await fetchJson("/api/shutdown");
        },

        // --- about ---

        async loadLogo() {
            if (this.logo) return;
            this.logo = await (await fetch("/logo", {
                credentials: "same-origin",
            })).text();
        },
    }));
});
