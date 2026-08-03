"""Validate OpenAPI YAML files against the OpenAPI specification."""

import argparse
import sys
from pathlib import Path

import yaml
from openapi_spec_validator import validate
from openapi_spec_validator.versions import shortcuts


def validate_yaml(file_path: str) -> bool:
    """Validate an OpenAPI YAML file and print results."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return False

    try:
        with open(path) as f:
            spec = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML format: {e}")
        return False

    if "openapi" not in spec:
        print("Error: Missing 'openapi' field in spec")
        return False

    version = str(spec["openapi"])
    print(f"OpenAPI version: {version}")
    print(f"Validating: {file_path}")

    try:
        validate(spec)
        print("Validation passed: OpenAPI spec is valid")
        return True
    except Exception as e:
        print(f"Validation failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validate OpenAPI YAML files")
    parser.add_argument("file", nargs="?", help="Path to the OpenAPI YAML file")
    parser.add_argument("--stdin", action="store_true", help="Read YAML content from stdin")
    args = parser.parse_args()

    if args.stdin:
        content = sys.stdin.read()
        try:
            spec = yaml.safe_load(content)
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML format: {e}")
            sys.exit(1)

        if "openapi" not in spec:
            print("Error: Missing 'openapi' field in spec")
            sys.exit(1)

        version = str(spec["openapi"])
        print(f"OpenAPI version: {version}")

        try:
            validate(spec)
            print("Validation passed: OpenAPI spec is valid")
            sys.exit(0)
        except Exception as e:
            print(f"Validation failed: {e}")
            sys.exit(1)
    elif args.file:
        success = validate_yaml(args.file)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
