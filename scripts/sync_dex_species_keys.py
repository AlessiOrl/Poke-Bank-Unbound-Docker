"""Keep Pokédex link keys aligned with the game's canonical species IDs."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIES_IDS = ROOT / "data" / "species_id.txt"
DEX_SPECIES = ROOT / "static" / "dex_species.json"


def generated_bytes():
    constants = {}
    for key, value in re.findall(
        r"^(SPECIES_[A-Z0-9_]+)\s+(0x[0-9A-Fa-f]+)",
        SPECIES_IDS.read_text(encoding="utf-8"),
        re.MULTILINE,
    ):
        species_id = int(value, 16)
        if species_id in constants:
            raise ValueError(f"Duplicate species ID {species_id}: {key}")
        constants[species_id] = key

    original = DEX_SPECIES.read_bytes()
    dex = json.loads(original)
    missing = [species_id for species_id in dex if int(species_id) not in constants]
    if missing:
        raise ValueError(f"Dex entries missing species constants: {', '.join(missing)}")

    for species_id, entry in dex.items():
        entry["speciesKey"] = constants[int(species_id)]

    line_ending = "\r\n" if b"\r\n" in original else "\n"
    return json.dumps(dex, ensure_ascii=False, indent=2).replace("\n", line_ending).encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report whether the dex data needs updating")
    args = parser.parse_args()
    updated = generated_bytes()
    if args.check:
        if DEX_SPECIES.read_bytes() != updated:
            parser.exit(1, "Pokédex species keys are out of date. Run this script without --check.\n")
        print("Pokédex species keys are up to date.")
    else:
        DEX_SPECIES.write_bytes(updated)
        print("Updated Pokédex species keys.")


if __name__ == "__main__":
    main()
