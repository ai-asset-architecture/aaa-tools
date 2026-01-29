from enum import Enum
from typing import Set

class Capability(Enum):
    FS_READ = "FS_READ"
    FS_WRITE = "FS_WRITE"
    GOV_AUDIT = "GOV_AUDIT"
    GOV_RELEASE = "GOV_RELEASE"

class CapabilityPack:
    def __init__(self, name: str, capabilities: Set[Capability]):
        self.name = name
        self.capabilities = capabilities

    def has(self, cap: Capability) -> bool:
        return cap in self.capabilities

    def __repr__(self):
        return f"CapabilityPack({self.name})"

# v2.0.1 Standard Packs
DEFAULT_PACK = CapabilityPack("default", {Capability.FS_READ, Capability.GOV_AUDIT})
ADMIN_PACK = CapabilityPack("admin", set(Capability))
