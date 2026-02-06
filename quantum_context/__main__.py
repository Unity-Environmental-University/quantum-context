#!/usr/bin/env python3
"""
Quantum Context CLI

Command-line interface for quantum-context knowledge graph.

Usage:
    quantum-context observe <subject>
    quantum-context analyze <subject>
    quantum-context record <subject> <predicate> <object> [--confidence CONF] [--evidence URL...]
    quantum-context list
    quantum-context export [--format json|ndjson]
"""

import argparse
import json
import sys
from pathlib import Path

from quantum_context import observe_context, analyze_dependencies, act_record
from quantum_context.core import GRAPH_FILE, _load_all_measurements


def cmd_observe(args):
    """Observe context about a subject."""
    result = observe_context(args.subject, observer=args.observer)

    print(f"Context for '{result.entity}':")
    print(f"  Magnitude: {result.magnitude:.2f}")
    print(f"  Coefficients: {result.coefficients}")

    if result.magnitude == 0:
        print(f"  (No measurements found)")
    else:
        print(f"\n  Confidence level: {'High' if result.magnitude > 0.7 else 'Moderate' if result.magnitude > 0.4 else 'Low'}")


def cmd_analyze(args):
    """Analyze dependencies for a subject."""
    result = analyze_dependencies(args.subject, independence_threshold=args.threshold)

    print(f"Dependencies for '{result.subject}':")

    if result.depends_on:
        print(f"\n  Depends on ({len(result.depends_on)}):")
        for dep in result.depends_on:
            conf = result.shared_structure.get(dep, 0)
            print(f"    - {dep} (confidence: {conf:.2f})")
    else:
        print(f"  (No dependencies found)")

    if result.independent_of:
        print(f"\n  Independent of ({len(result.independent_of)}):")
        for indep in result.independent_of:
            print(f"    - {indep}")
    else:
        print(f"  (No independent concepts detected)")


def cmd_record(args):
    """Record a new measurement."""
    # Confirmation required for recording
    if not args.yes:
        print(f"Record: {args.subject} {args.predicate} {args.object}")
        print(f"  Confidence: {args.confidence}")
        print(f"  Observer: {args.observer}")
        if args.evidence:
            print(f"  Evidence: {', '.join(args.evidence)}")

        response = input("\nConfirm? [y/N] ").strip().lower()
        if response not in ['y', 'yes']:
            print("Cancelled.")
            return

    result = act_record(
        args.subject,
        args.predicate,
        args.object,
        confidence=args.confidence,
        observer=args.observer,
        evidence=args.evidence or [],
        confirm=True
    )

    print(f"✓ {result['message']}")


def cmd_list(args):
    """List all measurements."""
    measurements = _load_all_measurements()

    if not measurements:
        print("No measurements found.")
        return

    # Group by subject
    by_subject = {}
    for m in measurements:
        subj = m['subject']
        if subj not in by_subject:
            by_subject[subj] = []
        by_subject[subj].append(m)

    print(f"Total measurements: {len(measurements)}")
    print(f"Subjects: {len(by_subject)}")
    print()

    for subject in sorted(by_subject.keys()):
        ms = by_subject[subject]
        print(f"  {subject} ({len(ms)} measurements)")
        if args.verbose:
            for m in ms:
                print(f"    - {m['predicate']} {m['object']} (conf={m['confidence']}, observer={m['observer']})")


def cmd_export(args):
    """Export measurements."""
    measurements = _load_all_measurements()

    if args.format == 'json':
        # Pretty JSON
        print(json.dumps(measurements, indent=2))
    else:
        # NDJSON (default)
        for m in measurements:
            print(json.dumps(m))


def main():
    parser = argparse.ArgumentParser(
        description="Quantum Context - Observer-relative knowledge graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # observe command
    observe_parser = subparsers.add_parser('observe', help='Observe context about a subject')
    observe_parser.add_argument('subject', help='Subject to observe')
    observe_parser.add_argument('--observer', default='claude', help='Observer frame (default: claude)')

    # analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze dependencies')
    analyze_parser.add_argument('subject', help='Subject to analyze')
    analyze_parser.add_argument('--threshold', type=float, default=0.3,
                               help='Independence threshold (default: 0.3)')

    # record command
    record_parser = subparsers.add_parser('record', help='Record a new measurement')
    record_parser.add_argument('subject', help='Subject')
    record_parser.add_argument('predicate', help='Predicate (e.g., "requires", "uses")')
    record_parser.add_argument('object', help='Object')
    record_parser.add_argument('--confidence', type=float, default=0.5,
                              help='Confidence (0.0-1.0, default: 0.5)')
    record_parser.add_argument('--observer', default='claude', help='Observer (default: claude)')
    record_parser.add_argument('--evidence', nargs='+', help='Evidence URLs')
    record_parser.add_argument('-y', '--yes', action='store_true',
                              help='Skip confirmation prompt')

    # list command
    list_parser = subparsers.add_parser('list', help='List all measurements')
    list_parser.add_argument('-v', '--verbose', action='store_true',
                            help='Show detailed information')

    # export command
    export_parser = subparsers.add_parser('export', help='Export measurements')
    export_parser.add_argument('--format', choices=['json', 'ndjson'], default='ndjson',
                              help='Export format (default: ndjson)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to command handlers
    commands = {
        'observe': cmd_observe,
        'analyze': cmd_analyze,
        'record': cmd_record,
        'list': cmd_list,
        'export': cmd_export,
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
