from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Block:
    block_id: str
    index: int
    text: str
    start_offset: int
    end_offset: int
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    kind: str = "narration"


@dataclass(frozen=True)
class BlockManifest:
    source_path: str
    source_sha256: str
    parser_version: str
    config: dict[str, object]
    blocks: list[Block]

    def to_dict(self) -> dict[str, object]:
        return {
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "parser_version": self.parser_version,
            "config": self.config,
            "blocks": [asdict(block) for block in self.blocks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "BlockManifest":
        blocks_data = data.get("blocks", [])
        return cls(
            source_path=str(data["source_path"]),
            source_sha256=str(data["source_sha256"]),
            parser_version=str(data["parser_version"]),
            config=dict(data.get("config", {})),
            blocks=[Block(**block_data) for block_data in blocks_data],
        )
