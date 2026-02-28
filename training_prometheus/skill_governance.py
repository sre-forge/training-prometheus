from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json

from .models import EnvironmentDescriptor, GovernanceMetadata, SemanticMapping, StabilityReport


class PromSkillGovernance:
    def build_metadata(
        self,
        descriptor: EnvironmentDescriptor,
        mapping: SemanticMapping,
        stability: StabilityReport,
    ) -> GovernanceMetadata:
        checksum = self._build_checksum(mapping, stability)
        return GovernanceMetadata(
            schema_version="1",
            generated_at=datetime.now(timezone.utc).isoformat(),
            descriptor_fingerprint=descriptor.deterministic_fingerprint(),
            artifact_checksum=checksum,
        )

    @staticmethod
    def _build_checksum(mapping: SemanticMapping, stability: StabilityReport) -> str:
        payload = json.dumps(
            {
                "mapping": asdict(mapping),
                "stability": asdict(stability),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256(payload.encode("utf-8")).hexdigest()
