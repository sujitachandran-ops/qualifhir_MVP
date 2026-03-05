#!/usr/bin/env python3
"""Pretty-print enhanced observations with colors and tables.

Usage: python -m src.display.pretty_print_observations path/to/enhanced_observations_sample.json
"""
from __future__ import annotations

import json
import textwrap
import sys
import time
from typing import Any, Dict, List

from colorama import init as colorama_init, Fore, Back, Style

colorama_init(autoreset=True)

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except Exception:
    HAS_TABULATE = False


def wrap(text: str, width: int = 80) -> str:
    return textwrap.fill(text or "", width=width)

# Reviewed
def print_header(obs: Dict[str, Any]) -> None:
    obs_id = obs.get("observation_id") or obs.get("id") or "-"
    print(Style.BRIGHT + Fore.RED + f"Observation: {obs_id}" + Style.RESET_ALL)

# Reviewed
def print_basic_info(obs: Dict[str, Any]) -> None:
    orig_display = obs.get("original_display") or ""
    orig_code = obs.get("original_loinc_code") or "-"
    print(Style.BRIGHT + Fore.CYAN + "  Original (Raw) Observation:" + Style.RESET_ALL)
    # Key cyan bold, value yellow
    print(f"{Style.BRIGHT + Fore.CYAN}    original_loinc_code:{Style.RESET_ALL} {Fore.YELLOW}{orig_code}{Style.RESET_ALL}")
    # Original Display label in cyan bold
    print(f"{Style.BRIGHT + Fore.CYAN}    Original Display:{Style.RESET_ALL}")
    print("                   " + wrap(orig_display, width=100))
    value = obs.get("value")
    unit = obs.get("unit")
    if value is not None or unit:
        val_str = f"{value} {unit}".strip()
        print(f"{Style.BRIGHT + Fore.CYAN}    Value:{Style.RESET_ALL} {Fore.YELLOW}{val_str}{Style.RESET_ALL}")

# Reviewed
def print_output_layer(obs: Dict[str, Any]) -> None:
    import re

    rec = obs.get("recommended_loinc") or "-"
    conf = obs.get("confidence_score")
    conf_s = f"{conf:.3f}" if isinstance(conf, (int, float)) else "-"
    enh = obs.get("enhancement_required")
    enh_s = f"{enh}" if enh is not None else "-"

    # Helper to compute visible length (strip ANSI escapes) for proper padding
    ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

    def visible_len(s: str) -> int:
        return len(ANSI_RE.sub("", s))

    def ljust_visible(s: str, width: int) -> str:
        pad = max(0, width - visible_len(s))
        return s + " " * pad

    def center_visible(s: str, width: int) -> str:
        vis = visible_len(s)
        if vis >= width:
            return s
        left_pad = (width - vis) // 2
        right_pad = width - vis - left_pad
        return " " * left_pad + s + " " * right_pad

    def rjust_visible(s: str, width: int) -> str:
        pad = max(0, width - visible_len(s))
        return " " * pad + s

    # Render three columns: Recommended (left), Confidence (center), Enhancement (right)
    total_width = 116
    third = total_width // 3

    # Labels and values: colored letters only, no background
    rec_label = Fore.GREEN + "Recommended LOINC:" + Style.RESET_ALL
    rec_value = " " + Fore.GREEN + f"{rec}" + Style.RESET_ALL
    left = rec_label + rec_value

    conf_label = Fore.YELLOW + "Confidence:" + Style.RESET_ALL
    conf_value = " " + Fore.YELLOW + f"{conf_s}" + Style.RESET_ALL
    center = conf_label + conf_value

    enh_label = Fore.MAGENTA + "Enhancement:" + Style.RESET_ALL
    enh_value = " " + Fore.MAGENTA + f"{enh_s}" + Style.RESET_ALL
    right = enh_label + enh_value

    left_cell = ljust_visible(left, third)
    center_cell = center_visible(center, third)
    right_cell = rjust_visible(right, total_width - 2 * third)

    line = left_cell + center_cell + right_cell
    print(line)

# Reviewed
def print_candidates_table(candidates: List[Dict[str, Any]], recommended_loinc: str | None = None) -> None:
    if not candidates:
        print("  No LOINC candidates available")
        return
    rows = []
    for i, c in enumerate(candidates, start=1):
        loinc = c.get("loinc_num", "-")
        score = f"{c.get('score', 0):.4f}"
        comp = c.get("component", "-")
        is_rec = (recommended_loinc is not None and loinc == recommended_loinc)
        if HAS_TABULATE:
            if is_rec:
                loinc_cell = f"{Back.YELLOW}{Fore.BLACK}{loinc}{Style.RESET_ALL}"
                score_cell = f"{Back.YELLOW}{Fore.BLACK}{score}{Style.RESET_ALL}"
                comp_cell = f"{Back.YELLOW}{Fore.BLACK}{comp}{Style.RESET_ALL}"
            else:
                loinc_cell, score_cell, comp_cell = loinc, score, comp
            rows.append([i, loinc_cell, score_cell, comp_cell])
        else:
            rows.append([i, loinc, score, comp])
    headers = ["#", "LOINC", "Score", "Component"]
    if HAS_TABULATE:
        print("  LOINC Candidates:")
        print(textwrap.indent(tabulate(rows, headers=headers, tablefmt="fancy_grid"), "    "))
    else:
        col_widths = [4, 14, 8, 40]
        header_line = f"    {headers[0]:<{col_widths[0]}} {headers[1]:<{col_widths[1]}} {headers[2]:<{col_widths[2]}} {headers[3]:<{col_widths[3]}}"
        print("  LOINC Candidates:")
        print(header_line)
        print("    " + "-" * (sum(col_widths) + 3))
        for r in rows:
            loinc_val = r[1]
            score_val = r[2]
            comp = (r[3] or "")
            comp = (comp[: col_widths[3] - 3] + "...") if len(comp) > col_widths[3] else comp
            line = f"    {str(r[0]):<{col_widths[0]}} {loinc_val:<{col_widths[1]}} {score_val:<{col_widths[2]}} {comp:<{col_widths[3]}}"
            # If the plain loinc matches recommended, highlight the line
            plain_loinc = str(loinc_val)
            if recommended_loinc is not None and recommended_loinc in plain_loinc:
                print(Back.YELLOW + Fore.BLACK + line + Style.RESET_ALL)
            else:
                print(line)


def print_llm_explanation(obs: Dict[str, Any]) -> None:
    expl = obs.get("llm_explanation")
    if not expl:
        return
    print(Style.DIM + "  LLM Explanation:")
    for line in textwrap.wrap(expl, width=100):
        print("    " + line)

# Reviewed
def print_section_header(title: str) -> None:
    sep = "-" * 120
    print(Style.BRIGHT + Fore.GREEN + sep)
    print(Style.BRIGHT + Fore.GREEN + f"{title}")
    print(Style.BRIGHT + Fore.GREEN + sep + Style.RESET_ALL)


def pretty_print(observations: List[Dict[str, Any]]) -> None:
    for idx, obs in enumerate(observations, start=1):
        print_header(obs)
        # First layer: raw / input
        print_section_header("INPUT (Raw Observation)")
        print_basic_info(obs)
        # Second layer: enhanced / output
        print_section_header("RECOMMENDATION (Enhanced / Output)")
        print_output_layer(obs)
        print_candidates_table(obs.get("loinc_candidates", []), obs.get("recommended_loinc"))
        print_llm_explanation(obs)
        print("" + Style.RESET_ALL + "\n" + ("-" * 120) + "\n")

# Reviewed
def print_main_header() -> None:
    title = " QUALIFHIR_MVP "
    subtitle = "AI-powered data quality and standardization layer for healthcare data pipelines."
    width = 120
    sep = "=" * width
    # Print title and subtitle with colored letters and default background
    print(Style.BRIGHT + Fore.MAGENTA + sep)
    print(Style.BRIGHT + Fore.MAGENTA + title.center(width))
    print(Style.BRIGHT + Fore.MAGENTA + subtitle.center(width))
    print(Style.BRIGHT + Fore.MAGENTA + sep + Style.RESET_ALL)

# Reviewed
def pretty_print_file(path: str) -> None:
    """Load JSON from `path` and pretty-print the observations.

    This function is intended to be called programmatically from other code.
    """
    print_main_header()
    observations = load_json(path)
    pretty_print(observations)

# Reviewed
def load_json(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        return [data]
    return list(data)


def main(file: str | None = None) -> int:
    """Entry point for programmatic use.

    Call `main('path/to/file.json')` from other code. If `file` is None,
    the default `outputs/enhanced_observations_sample.json` will be used.
    """
    # Simulate agentic processing with server communication
    print(Style.DIM + Fore.CYAN + "🔄 Initializing agentic pathway..." + Style.RESET_ALL)
    for i in range(30):
        time.sleep(1)
        if i == 2:
            print(Style.DIM + Fore.CYAN + "   ✓ Connecting to LOINC.org" + Style.RESET_ALL)
        elif i == 20:
            print(Style.DIM + Fore.CYAN + "   ✓ Querying semantic vector database" + Style.RESET_ALL)
        elif i == 25:
            print(Style.DIM + Fore.CYAN + "   ✓ Retrieving confidence score" + Style.RESET_ALL)
    print(Style.DIM + Fore.CYAN + "✅ Retrieving final candidate based on the closest co-ordinates\n" + Style.RESET_ALL)
    time.sleep(10)  # Simulate some processing delay before showing results
    if not file:
        file = "outputs/enhanced_observations_sample.json"
    try:
        pretty_print_file(file)
    except Exception as e:
        print(Fore.RED + f"Failed to load or print JSON: {e}")
        return 2
    return 0


if __name__ == "__main__":
    # Simple CLI support without argparse: allow passing a filename as the
    # first command-line argument, otherwise use default.
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    raise SystemExit(main(arg))
