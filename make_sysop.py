#!/usr/bin/env python3
"""Grant or revoke sysop privileges for a CompuServe simulator member.

Usage:
    python3 make_sysop.py USER_ID            # grant sysop
    python3 make_sysop.py --revoke USER_ID   # revoke sysop

Run from the repository directory. The member must already exist
(create the account by logging in once first).
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import compuserve


def main(argv):
    revoke = "--revoke" in argv
    args = [a for a in argv if a != "--revoke"]
    if len(args) != 1:
        print("Usage: make_sysop.py [--revoke] USER_ID")
        return 2
    user_id = args[0]
    compuserve.initialize_database()
    profile = compuserve.profiles.get(user_id)
    if profile is None:
        print(f"Unknown user id: {user_id!r}")
        known = sorted(compuserve.profiles)
        if known:
            print("Known user ids:", ", ".join(known))
        return 1
    profile["is_sysop"] = not revoke
    compuserve.save_profiles()
    print(f"{'Revoked' if revoke else 'Granted'} sysop privileges for {user_id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
