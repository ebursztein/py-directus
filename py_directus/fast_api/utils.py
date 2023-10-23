import asyncio
from enum import Enum
from typing import Optional, List

from py_directus.models import Role
from py_directus import Directus

from .globals import (
    directus_session, 
    directus_url, 
    directus_admin, 
    cached_directus_instances
)


async def get_directus_login(email: str, password: str) -> Directus:
    d = await Directus(directus_url, connection=directus_session, email=email, password=password)
    cached_directus_instances[d.token] = d
    return d


async def get_directus_from_token(access_token, refresh_token=None) -> Optional[Directus]:
    directus = await Directus(directus_url, token=access_token, refresh_token=refresh_token, connection=directus_session)
    await directus.user  # noqa
    return directus


async def directus_logout(directus: Directus):
    cached_directus_instances.pop(directus.token, None)
    await directus.logout()


class Roles(str, Enum):
    ADMIN = "Administrator"
    COMPANY = "Company"
    LICENSE = "License"
    CREDIT = "Credit"
    DEVICE = "Device"
    PARTNER = "Partner"


class RoleToID:
    def __init__(self):
        self.roles: List[Role] | None = None

    def __await__(self):
        async def closure():
            # Perform login when credentials are present and no token
            await directus_admin
            roles = await directus_admin.collection(Role).read()
            self.roles = {role.name: role.id for role in roles.items}
            return self

        return closure().__await__()

    def __call__(self, role: str | Roles) -> [str]:  # noqa
        if isinstance(role, Roles):
            role = role.value
        return [self.roles[role]]


role_to_id = RoleToID()
