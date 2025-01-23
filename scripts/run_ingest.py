#!/usr/bin/env python3
import argparse
import asyncio
from typing import Optional
from eaia.email_service import fetch_group_emails
from eaia.main.config import get_config
from langgraph_sdk import get_client
import httpx
import uuid
import hashlib


async def main(
    url: Optional[str] = None,
    minutes_since: int = 60,
    email_token: Optional[str] = None,
    email_secret: Optional[str] = None,
    early: bool = True,
    rerun: bool = False,
    email: Optional[str] = None,
    service: str = "gmail",
):
    if email is None:
        email_address = get_config({"configurable": {}})["email"]
    else:
        email_address = email
    if url is None:
        client = get_client(url="http://127.0.0.1:2024")
    else:
        client = get_client(
            url=url
        )

    # TODO: This really should be async
    for email in fetch_group_emails(
        email_address,
        minutes_since=minutes_since,
        service=service,
        gmail_token=email_token,
        gmail_secret=email_secret,
    ):
        thread_id = str(
            uuid.UUID(hex=hashlib.md5(email["thread_id"].encode("UTF-8")).hexdigest())
        )
        try:
            thread_info = await client.threads.get(thread_id)
        except httpx.HTTPStatusError as e:
            if "user_respond" in email:
                continue
            if e.response.status_code == 404:
                thread_info = await client.threads.create(thread_id=thread_id)
            else:
                raise e
        if "user_respond" in email:
            await client.threads.update_state(thread_id, None, as_node="__end__")
            continue
        recent_email = thread_info["metadata"].get("email_id")
        if recent_email == email["id"]:
            if early:
                break
            else:
                if rerun:
                    pass
                else:
                    continue
        await client.threads.update(thread_id, metadata={"email_id": email["id"]})

        await client.runs.create(
            thread_id,
            "main",
            input={"email": email},
            multitask_strategy="rollback",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        help="URL of the agent to connect to",
        default=None,
    )
    parser.add_argument(
        "--minutes-since",
        type=int,
        help="Number of minutes to look back",
        default=60,
    )
    parser.add_argument(
        "--email-token",
        type=str,
        help="Gmail token",
        default=None,
    )
    parser.add_argument(
        "--email-secret",
        type=str,
        help="Gmail secret",
        default=None,
    )
    parser.add_argument(
        "--early",
        action="store_true",
        help="Whether to early exit if there are no emails",
        default=True,
    )
    parser.add_argument(
        "--rerun",
        action="store_true",
        help="Whether to rerun all emails",
        default=False,
    )
    parser.add_argument(
        "--email",
        type=str,
        help="Email address to use",
        default=None,
    )
    parser.add_argument(
        "--service",
        type=str,
        choices=["gmail", "ms"],
        help="Email service to use (gmail or ms)",
        default="gmail",
    )
    args = parser.parse_args()
    asyncio.run(
        main(
            url=args.url,
            minutes_since=args.minutes_since,
            email_token=args.email_token,
            email_secret=args.email_secret,
            early=args.early,
            rerun=args.rerun,
            email=args.email,
            service=args.service,
        )
    )
