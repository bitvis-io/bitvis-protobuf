#!/usr/bin/env python3
"""Generate Python code from protobuf definitions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Generate protobuf Python code."""
    # Get project root
    project_root = Path(__file__).parent.parent
    proto_dir = project_root / "src" / "bitvis_protobuf" / "proto"
    output_dir = project_root / "src" / "bitvis_protobuf"

    if not proto_dir.exists():
        print(f"Error: Proto directory not found: {proto_dir}")
        return 1

    # Find all .proto files
    proto_files = list(proto_dir.glob("*.proto"))
    if not proto_files:
        print(f"Error: No .proto files found in {proto_dir}")
        return 1

    print(f"Found {len(proto_files)} proto files:")
    for proto_file in proto_files:
        print(f"  - {proto_file.name}")

    # Generate Python code using protoc
    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"--proto_path={proto_dir}",
        f"--python_out={output_dir}",
        f"--pyi_out={output_dir}",
    ] + [str(f) for f in proto_files]

    print(f"\nRunning protoc...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("\n✓ Protobuf code generated successfully!")

        # Fix absolute imports to relative imports in generated files
        import re
        for pb_file in output_dir.glob("*_pb2.py"):
            text = pb_file.read_text()
            fixed = re.sub(r"^import (\w+_pb2)", r"from . import \1", text, flags=re.MULTILINE)
            if fixed != text:
                pb_file.write_text(fixed)

        # List generated files
        print("\nGenerated files:")
        for pb_file in sorted(output_dir.glob("*_pb2.py*")):
            print(f"  - {pb_file.name}")

        return 0
    else:
        print(f"\n✗ Error generating protobuf code (exit code {result.returncode})")
        return result.returncode


if __name__ == "__main__":
    sys.exit(main())
