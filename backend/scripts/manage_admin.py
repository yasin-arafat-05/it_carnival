#!/usr/bin/env python3
"""
Terminal CLI script for assigning ADMIN role to users directly in the database.

Usage:
    python scripts/manage_admin.py promote --username yasin_arafat_05
    python scripts/manage_admin.py demote --username yasin_arafat_05
    python scripts/manage_admin.py list
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import argparse
import asyncio
from sqlalchemy import select, update
from app.database.session import asyncSession
from app.database.models.user import User


async def promote_user(username: str):
    async with asyncSession() as db:
        query = select(User).where(User.username == username)
        res = await db.execute(query)
        user = res.scalar_one_or_none()

        if not user:
            print(f"❌ ERROR: User with username '{username}' not found.")
            sys.exit(1)

        await db.execute(
            update(User).where(User.id == user.id).values(role="ADMIN")
        )
        await db.commit()
        print(f"✅ SUCCESS: User '{username}' ({user.email}) has been granted ADMIN role in the database.")


async def demote_user(username: str):
    async with asyncSession() as db:
        query = select(User).where(User.username == username)
        res = await db.execute(query)
        user = res.scalar_one_or_none()

        if not user:
            print(f"❌ ERROR: User with username '{username}' not found.")
            sys.exit(1)

        await db.execute(
            update(User).where(User.id == user.id).values(role="USER")
        )
        await db.commit()
        print(f"✅ SUCCESS: User '{username}' ({user.email}) role changed back to 'USER'.")


async def list_admins():
    async with asyncSession() as db:
        query = select(User).where(User.role == "ADMIN")
        res = await db.execute(query)
        admins = res.scalars().all()

        print("\n--- Current System Administrators ---")
        if not admins:
            print("No admin users found.")
        else:
            for a in admins:
                print(f"• ID: {a.id} | Username: @{a.username} | Email: {a.email} | Name: {a.full_name}")
        print("------------------------------------\n")


def main():
    parser = argparse.ArgumentParser(description="Terminal Database Admin Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Promote Command
    promote_parser = subparsers.add_parser("promote", help="Grant ADMIN role to user handle")
    promote_parser.add_argument("--username", required=True, help="Target username")

    # Demote Command
    demote_parser = subparsers.add_parser("demote", help="Revoke ADMIN role from user handle")
    demote_parser.add_argument("--username", required=True, help="Target username")

    # List Command
    subparsers.add_parser("list", help="List all current administrators")

    args = parser.parse_args()

    if args.command == "promote":
        asyncio.run(promote_user(args.username))
    elif args.command == "demote":
        asyncio.run(demote_user(args.username))
    elif args.command == "list":
        asyncio.run(list_admins())


if __name__ == "__main__":
    main()
