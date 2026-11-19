"""
Empirical Adversarial Test Suite for OptiLocal Autonomous PDF Engine
Target: modules/03_moteur_audit_ia/generateur_audit.py & modules/04_distribution_ventes/webhook_listener.py
Executed by: Teamwork Challenger 1 (Adversarial Critic)
"""

import os
import sys
import time
import re
from pathlib import Path
from pypdf import PdfReader

# Add module paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "modules" / "03_moteur_audit_ia"))
sys.path.insert(0, str(PROJECT_ROOT / "modules" / "04_distribution_ventes"))

from generateur_audit import generate_autonomous_pdf
from webhook_listener import generate_fallback_pdf


def assert_pdf_integrity(pdf_path: str, expected_pages: int = 4, min_size: int = 20_000, target_size: int = 300_000):
    """Programmatic assertions on generated PDF."""
    path = Path(pdf_path)
    assert path.exists(), f"PDF file does not exist: {pdf_path}"
    
    size = os.path.getsize(path)
    assert size >= min_size, f"PDF file size too small: {size} < {min_size} bytes"
    
    reader = PdfReader(str(path))
    assert len(reader.pages) == expected_pages, f"Page count mismatch: {len(reader.pages)} != {expected_pages}"
    
    # Text length per page (zero blank pages)
    full_text = ""
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        stripped = text.strip()
        assert len(stripped) >= 200, f"Page {idx+1} has insufficient text: {len(stripped)} chars (< 200)"
        full_text += " " + text
        
    # Check for Garantie Sérénité Artisan
    assert "Garantie Sérénité Artisan" in full_text, "Missing 'Garantie Sérénité Artisan' in PDF text"
    
    # Anti-AI and brand sanitation checks (word-boundary / semantic)
    assert not re.search(r'\bIA\b', full_text), "Forbidden standalone acronym 'IA' found in PDF text"
    assert not re.search(r'\bbot\b', full_text, re.IGNORECASE), "Forbidden word 'bot' found in PDF text"
    assert "intelligence artificielle" not in full_text.lower(), "Forbidden phrase 'intelligence artificielle' found"
    assert "autobiz" not in full_text.lower(), "Forbidden residual brand 'AutoBiz' found"
    
    return {
        "path": str(path),
        "size": size,
        "pages": len(reader.pages),
        "target_size_met": size >= target_size,
        "contains_territorial_ia_substring": "IA" in full_text  # Documenting substring behavior
    }


def run_all_tests():
    print("=" * 70)
    print("RUNNING EMPIRICAL ADVERSARIAL PDF ENGINE SUITE")
    print("=" * 70)
    
    results = {"passed": [], "failed": []}
    
    # -------------------------------------------------------------------------
    # Test Group 1: Baseline & Special Characters (DISPATCH §1.1 & §1.2)
    # -------------------------------------------------------------------------
    test_cases_autonomous = [
        ("Baseline Standard", "Plomberie Martin", "contact@martin.fr", 48, None),
        ("Special Chars & Accents & Emoji", "Plomberie & Chauffage / L'Étoile ✨", "etoile@test.fr", 48, None),
        ("HTML-like safe characters", "Plomberie & Sons & Co", "sons@test.fr", 48, None),
        ("Empty String Name", "", "empty@test.fr", 48, None),
        ("Whitespace String Name", "     ", "spaces@test.fr", 48, None),
        ("Long Name 200 Chars", "A" * 200, "long200@test.fr", 48, None),
        ("Score 0", "Entreprise Zéro", "zero@test.fr", 0, None),
        ("Score 100", "Entreprise Parfaite", "cent@test.fr", 100, None),
        ("Score -10", "Entreprise Négative", "neg@test.fr", -10, None),
        ("Score 150", "Entreprise Hors Bornes", "sur@test.fr", 150, None),
        ("Audit Data None", "Entreprise Sans Data", "nodata@test.fr", 48, None),
        ("Audit Data Empty Dict", "Entreprise Dict Vide", "emptydict@test.fr", 48, {}),
        ("Audit Data Partial Dict", "Entreprise Partielle", "partial@test.fr", 48, {"rating": 3.8}),
    ]
    
    for label, b_name, email, score, audit_data in test_cases_autonomous:
        try:
            pdf = generate_autonomous_pdf(b_name, email, audit_data=audit_data, score=score)
            res = assert_pdf_integrity(pdf)
            print(f"  [PASS] {label:35} -> Size: {res['size']} B, Pages: {res['pages']}")
            results["passed"].append(label)
        except Exception as e:
            print(f"  [FAIL] {label:35} -> Error: {type(e).__name__}: {e}")
            results["failed"].append((label, f"{type(e).__name__}: {e}"))
            
    # -------------------------------------------------------------------------
    # Test Group 2: Webhook Fallback Functionality (DISPATCH §1)
    # -------------------------------------------------------------------------
    test_cases_fallback = [
        ("Fallback Standard", "Artisan Menuiserie", "menuisier@test.fr", 52),
        ("Fallback Special Chars", "Plomberie & Chauffage / L'Étoile ✨", "etoile@test.fr", 48),
        ("Fallback Empty Name", "", "fallback_empty@test.fr", 48),
        ("Fallback Whitespace Name", "   ", "fallback_spaces@test.fr", 48),
        ("Fallback None Name", None, "fallback_none@test.fr", 48),
    ]
    
    for label, b_name, email, score in test_cases_fallback:
        try:
            pdf = generate_fallback_pdf(b_name, email, score=score)
            res = assert_pdf_integrity(pdf)
            print(f"  [PASS] {label:35} -> Size: {res['size']} B, Pages: {res['pages']}")
            results["passed"].append(label)
        except Exception as e:
            print(f"  [FAIL] {label:35} -> Error: {type(e).__name__}: {e}")
            results["failed"].append((label, f"{type(e).__name__}: {e}"))

    # -------------------------------------------------------------------------
    # Test Group 3: Adversarial Vulnerability Mining (Edge Cases)
    # -------------------------------------------------------------------------
    adversarial_edge_cases = [
        ("Adversarial: business_name=None", None, "none_name@test.fr", 48, None),
        ("Adversarial: audit_data rating=None", "Test Rating None", "t1@test.fr", 48, {"rating": None}),
        ("Adversarial: audit_data review_count=None", "Test Reviews None", "t2@test.fr", 48, {"review_count": None}),
        ("Adversarial: audit_data rating='N/A'", "Test Rating String", "t3@test.fr", 48, {"rating": "N/A"}),
        ("Adversarial: XML unclosed bracket '<IDF'", "Chauffage <IDF", "t4@test.fr", 48, None),
        ("Adversarial: Very long name (300 chars)", "A" * 300, "t5@test.fr", 48, None),
    ]

    for label, b_name, email, score, audit_data in adversarial_edge_cases:
        try:
            pdf = generate_autonomous_pdf(b_name, email, audit_data=audit_data, score=score)
            res = assert_pdf_integrity(pdf)
            print(f"  [UNEXPECTED PASS] {label:35} -> Size: {res['size']} B, Pages: {res['pages']}")
            results["passed"].append(label)
        except Exception as e:
            print(f"  [CONFIRMED FLAW] {label:35} -> {type(e).__name__}: {e}")
            results["failed"].append((label, f"{type(e).__name__}: {e}"))

    # -------------------------------------------------------------------------
    # Test Group 4: Sequential Performance Benchmark (5 PDFs)
    # -------------------------------------------------------------------------
    print("-" * 70)
    print("SEQUENTIAL PERFORMANCE BENCHMARK (5 PDFs)")
    t_start = time.time()
    perf_times = []
    for i in range(5):
        t0 = time.time()
        generate_autonomous_pdf(f"Perf Test #{i+1}", f"perf{i+1}@test.fr", score=45 + i*5)
        perf_times.append(time.time() - t0)
    total_time = time.time() - t_start
    avg_time = total_time / 5
    print(f"  Total duration: {total_time:.3f} s | Average: {avg_time:.3f} s/PDF")
    for i, t in enumerate(perf_times):
        print(f"  Run #{i+1}: {t:.3f} s")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("=" * 70)
    print(f"RESULTS: {len(results['passed'])} PASSED, {len(results['failed'])} FAILED/FLAWS")
    print("=" * 70)
    return results, avg_time


if __name__ == "__main__":
    results, avg_time = run_all_tests()
