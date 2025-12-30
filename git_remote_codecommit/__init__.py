# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import argparse
import datetime
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Set
from urllib.parse import urlparse, quote

import botocore.auth
import botocore.awsrequest
import botocore.hooks
import botocore.session
from botocore.credentials import JSONFileCache


# =========================
# Constants
# =========================

CODECOMMIT_SERVICE = "codecommit"
PROTOCOL_VERSION = "v1"
REGION_PATTERN = re.compile(r"^[a-z]{2}-[a-z0-9-]+-\d+$")
__version__ = "2.0.0"


# =========================
# Exceptions
# =========================


class FormatError(Exception):
    pass


class ProfileNotFound(Exception):
    pass


class RegionNotFound(Exception):
    pass


class RegionNotAvailable(Exception):
    pass


class CredentialsNotFound(Exception):
    pass


# =========================
# Context
# =========================


@dataclass(frozen=True)
class Context:
    session: botocore.session.Session
    repository: str
    version: str
    region: str
    credentials: botocore.credentials.Credentials

    @staticmethod
    def from_url(remote_url: str) -> "Context":
        url = urlparse(remote_url)

        if not url.scheme or not url.netloc:
            raise FormatError(
                f"Malformed URL: {remote_url}. "
                "Expected: codecommit://<profile>@<repo> "
                "or codecommit::<region>://<profile>@<repo>"
            )

        profile = os.getenv("AWS_PROFILE", "default")
        repository = url.netloc

        event_handler = botocore.hooks.HierarchicalEmitter()

        if "@" in url.netloc:
            profile, repository = url.netloc.split("@", 1)
            session = botocore.session.Session(
                profile=profile,
                event_hooks=event_handler,
            )

            if profile not in session.available_profiles:
                raise ProfileNotFound(
                    f"Profile '{profile}' not found. "
                    f"Available profiles: {', '.join(session.available_profiles)}"
                )
        else:
            session = botocore.session.Session(event_hooks=event_handler)

        # Enable assume-role cache
        session.get_component("credential_provider").get_provider(
            "assume-role"
        ).cache = JSONFileCache()

        available_regions: Set[str] = {
            region
            for partition in session.get_available_partitions()
            for region in session.get_available_regions(
                CODECOMMIT_SERVICE,
                partition,
            )
        }

        # Resolve region
        if url.scheme == CODECOMMIT_SERVICE:
            region = session.get_config_variable("region")
            if not region:
                raise RegionNotFound(
                    f"Profile '{profile}' does not have a region configured"
                )

        elif REGION_PATTERN.match(url.scheme):
            region = url.scheme
        else:
            raise FormatError(f"Invalid scheme in URL: {remote_url}")

        if region not in available_regions:
            raise RegionNotAvailable(
                f"Region '{region}' is not available for AWS CodeCommit"
            )

        credentials = session.get_credentials()
        if not credentials:
            raise CredentialsNotFound(
                f"No credentials configured for profile '{profile}'"
            )

        return Context(
            session=session,
            repository=repository,
            version=PROTOCOL_VERSION,
            region=region,
            credentials=credentials,
        )


# =========================
# Git URL & Signing
# =========================


def website_domain_mapping(region: str) -> str:
    return "amazonaws.com.cn" if region.startswith("cn-") else "amazonaws.com"


def git_url(
    repository: str,
    version: str,
    region: str,
    credentials,
) -> str:
    hostname = os.getenv(
        "CODE_COMMIT_ENDPOINT",
        f"git-codecommit.{region}.{website_domain_mapping(region)}",
    )

    path = f"/{version}/repos/{repository}"

    token = f"%{credentials.token}" if credentials.token else ""
    username = quote(credentials.access_key + token, safe="")

    signature = sign(hostname, path, region, credentials)

    return f"https://{username}:{signature}@{hostname}{path}"


def sign(
    hostname: str,
    path: str,
    region: str,
    credentials,
) -> str:
    request = botocore.awsrequest.AWSRequest(
        method="GIT",
        url=f"https://{hostname}{path}",
    )

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")

    request.context["timestamp"] = timestamp

    signer = botocore.auth.SigV4Auth(
        credentials,
        CODECOMMIT_SERVICE,
        region,
    )

    canonical_request = f"GIT\n{path}\n\n" f"host:{hostname}\n\n" "host\n"

    string_to_sign = signer.string_to_sign(
        request,
        canonical_request,
    )

    signature = signer.signature(string_to_sign, request)

    return f"{timestamp}Z{signature}"


# =========================
# CLI
# =========================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="git-remote-codecommit",
        description="Git remote helper for AWS CodeCommit",
        add_help=False
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "git_command",
        help="Git command (e.g. pull,fetch, push)",
    )

    parser.add_argument(
        "remote_url",
        help="CodeCommit remote URL",
    )

    return parser.parse_args()


def main() -> None:
    try:
        args = parse_args()

        if args.git_command == "version":
            print(__version__)
            return
        
        if not args.git_command or not args.remote_url:
            sys.exit(
                "Usage: git-remote-codecommit <git_command> <remote_url>"
            )

        context = Context.from_url(args.remote_url)
        authenticated_url = git_url(
            context.repository,
            context.version,
            context.region,
            context.credentials,
        )
        env = os.environ.copy()
        env["GIT_CONFIG_COUNT"] = "1"
        env["GIT_CONFIG_KEY_0"] = "credential.helper"
        env["GIT_CONFIG_VALUE_0"] = ""
        result = subprocess.run(
            ["git", "remote-http", args.git_command, authenticated_url],
            stdout=sys.stdout,
            stderr=sys.stderr,
            check=False,
            env=env
        )

        sys.exit(result.returncode)

    except (
        FormatError,
        ProfileNotFound,
        RegionNotFound,
        RegionNotAvailable,
        CredentialsNotFound,
    ) as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main()
