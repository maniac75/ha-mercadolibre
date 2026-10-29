"""Build a deterministic install archive using an explicit file allowlist."""

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components/mercadolibre_tracking"


def main():
    manifest = json.loads((COMPONENT / "manifest.json").read_text())
    version = manifest["version"]
    assert manifest["domain"] == "mercadolibre_tracking"
    files = [
        p
        for p in COMPONENT.rglob("*")
        if p.is_file() and p.suffix in {".py", ".json", ".png", ".yaml"} and "__pycache__" not in p.parts
    ]
    files += [
        ROOT / n
        for n in (
            "README.md",
            "LICENSE",
            "docs/INSTALL.md",
            "docs/AUTHORIZATION.md",
            "docs/mercadolibre-card.yaml",
            "docs/images/card-example.png",
        )
    ]
    for path in files:
        assert not path.is_symlink()
        if path.suffix == ".py":
            compile(path.read_text(), str(path.relative_to(ROOT)), "exec")
        elif path.suffix == ".json":
            json.loads(path.read_text())
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    archive = destination / f"mercadolibre_tracking-{version}.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as output:
        for path in sorted(files):
            info = ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, path.read_bytes())
    with ZipFile(archive) as package:
        assert package.testzip() is None
        assert all(not name.startswith(("/", "../")) for name in package.namelist())
        assert not any(
            ".storage" in name or ".venv" in name or name.startswith("tests/") for name in package.namelist()
        )
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = destination / f"{archive.name}.sha256"
    checksum.write_text(f"{digest}  {archive.name}\n")
    print(json.dumps({"archive": str(archive), "sha256": digest, "files": len(files), "checksum": str(checksum)}))


if __name__ == "__main__":
    main()
