from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppContext:
    """Application filesystem context."""

    root_path: Path
    installers_dir_name: str = "Instaladores"
    tools_dir_name: str = "Herramientas"

    @property
    def installers_path(self) -> Path:
        return self.root_path / self.installers_dir_name

    @property
    def tools_path(self) -> Path:
        return self.root_path / self.tools_dir_name
