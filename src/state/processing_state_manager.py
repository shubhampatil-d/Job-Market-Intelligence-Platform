import json
from pathlib import Path, PurePosixPath
from typing import Iterable


class ProcessingStateManager:
    """Track raw files successfully processed by the processing pipeline."""

    def __init__(
        self,
        state_file: str | Path = "state/processing_state.json",
    ):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _key(file_path: str | Path) -> str:
        # Normalize separators so Windows and Linux paths match.
        normalized = str(file_path).replace("\\", "/")
        parts = PurePosixPath(normalized).parts

        # Use the path relative to the raw directory as a stable identifier.
        raw_indices = [
            index for index, part in enumerate(parts)
            if part.casefold() == "raw"
        ]

        if raw_indices:
            relative_parts = parts[raw_indices[-1] + 1:]
            return "raw/" + "/".join(relative_parts).casefold()

        # Fallback for paths outside a raw directory.
        return normalized.casefold()

    def load(self) -> dict:
        if not self.state_file.exists():
            return {"processed_files": []}

        with self.state_file.open("r", encoding="utf-8") as file:
            state = json.load(file)

        if not isinstance(state.get("processed_files"), list):
            raise ValueError(
                "Invalid processing checkpoint: processed_files must be a list"
            )

        return state

    def filter_unprocessed(
        self,
        files: Iterable[str | Path],
    ) -> list[Path]:
        state = self.load()
        processed = {
            self._key(path)
            for path in state["processed_files"]
        }

        return [
            Path(path)
            for path in files
            if self._key(path) not in processed
        ]

    def mark_processed(
        self,
        files: Iterable[str | Path],
    ) -> None:
        state = self.load()
        processed = {
            self._key(path)
            for path in state["processed_files"]
        }

        processed.update(self._key(path) for path in files)
        state["processed_files"] = sorted(processed)

        # Replace the checkpoint atomically to avoid partial JSON writes.
        temporary_path = self.state_file.with_suffix(".tmp")

        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(state, file, indent=4)

        temporary_path.replace(self.state_file)
