---
phase: 01c-character-training-system
plan: 02
type: execute
wave: 2
depends_on: ["01c-01"]
files_modified:
  - src/training_engine/benchmark.py
  - src/training_engine/scorer_adapter.py
  - src/training_engine/__init__.py
  - tests/test_lora_training.py
autonomous: true
requirements:
  - CHAR-07
user_setup: []
must_haves:
  truths:
    - Plugging the real IdentityScorer into LoRABenchmark yields correctly weighted composites — no zero-dimension collapse from key mismatch (G11, G12 fixed)
    - Benchmark weights are sourced from the identity-engine plugin registry per D-06 and sum to 1.00 across the seven canonical dimensions (locked decision)
    - Pass gate requires composite >= 0.90 AND full weight coverage, implementing the ROADMAP >= 90% consistency requirement (G13 + A7 honesty)
    - IdentityScorerProvider adapts identity_engine.IdentityScorer to the ScorerProvider protocol offline via light mode, dropping unknown plugin keys defensively
  artifacts:
    - src/training_engine/benchmark.py (canonical weight table, threshold 0.90, coverage-aware evaluate)
    - src/training_engine/scorer_adapter.py (new IdentityScorerProvider)
    - src/training_engine/__init__.py (re-exports updated)
    - tests/test_lora_training.py (adapter fixture tests, threshold/coverage cases, drift guard)
  key_links:
    - scorer_adapter returns plugin-name keys; benchmark._BENCHMARK_WEIGHTS keys are the SAME plugin names — the adapter needs no renaming map because weights were aligned onto plugin names (research Pattern 1 recommended direction)
    - MockScorerProvider emits the same seven canonical keys so determinism tests stay meaningful against the real adapter's output shape
    - IdentityScorer(light=True) construction works offline (numpy/PIL plugins only) — torch-backed plugins stay out of the unit path (C-OFFLINE)
---

<objective>
Bridge the identity engine into the LoRA quality benchmark (CHAR-07 criterion 4): align benchmark dimension names and weights onto the identity-engine plugin registry per D-06, raise the pass threshold to the locked 0.90, make partial-plugin-coverage honest instead of silent composite dilution, and deliver the IdentityScorerProvider adapter.

Purpose: Today, plugging the real scorer in would produce a composite near zero because five of six benchmark weight keys match no plugin name — every lookup misses. This plan makes the >= 0.90 production gate legally bind to what the identity engine actually measures.
Output: Aligned benchmark.py, new scorer_adapter.py, updated tests.
</objective>

<execution_context>
@/root/.config/opencode/gsd-core/workflows/execute-plan.md
@/root/.config/opencode/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/01c-character-training-system/01c-CONTEXT.md
@.planning/phases/01c-character-training-system/01c-RESEARCH.md
@.planning/phases/01c-character-training-system/01c-PATTERNS.md

@src/training_engine/benchmark.py
@src/identity_engine/scorer.py
@tests/test_lora_training.py

Phase constraints (echoed in every action):
- C-OFFLINE: all tests pass without GPU/network — light-mode scorer only, frozen fixtures, tmp_path images.
- C-CATALOGDB: this plan never touches catalog.db.
- C-NODEP: stdlib-only plus already-declared deps (Pillow/numpy). No new packages.
- Report byte-compatibility constraints do NOT apply to this phase (Phase 7/8 scope).

Resolved assumptions binding this plan:
- A2 resolved by user decision: canonical weights = identity-engine plugin registry weights (D-06 source), NOT BrandScore.WEIGHTS (whose technical_quality dimension is emitted by no plugin and would cap achievable totals at 0.85).
- A7 resolved by design: partial coverage (light mode drops DINOv2/CLIP-backed dims) is surfaced explicitly via weight_coverage and fails the gate rather than silently renormalizing a "Brand Score" that is not one.
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Align benchmark onto identity-engine plugin names/weights, threshold 0.90, coverage-honest evaluation (G11, G12, G13, A7)</name>
  <files>src/training_engine/benchmark.py, tests/test_lora_training.py</files>
  <read_first>
    @src/training_engine/benchmark.py (_BENCHMARK_WEIGHTS L148-155 legacy table; BenchmarkConfig L40 threshold; evaluate() L263-309 composite loop — note all_dim_scores.get(dim_name, [0.0]) zero-default dilution at L271 and unconditional weight_total accumulation at L290; BenchmarkResult dataclass; report(); MockScorerProvider L118-141)
    @src/identity_engine/scorer.py (plugin name/weight attributes L69-81 — the canonical source of truth being mirrored)
    @.planning/phases/01c-character-training-system/01c-RESEARCH.md (G11-G14 rows; Pattern 1 weight-direction recommendation; Pitfall 4)
  </read_first>
  <behavior>
    - Frozen fixture provider returning all seven canonical dims with known values: composite equals the hand-computed weighted average (weights sum 1.00), passed=True when composite >= 0.90.
    - Same fixture missing character_consistency and prompt_accuracy (light-mode simulation): those dims are excluded entirely — composite is the weighted average over present dims only, weight_coverage < 1.0, passed=False regardless of composite value.
    - Composite exactly 0.8999 with full coverage → passed=False; boundary behavior matches strict >= threshold comparison.
    - MockScorerProvider determinism: identical seeds produce identical seven-key dicts; different seeds differ.
  </behavior>
  <action>
    Replace `_BENCHMARK_WEIGHTS` with the canonical seven-dimension table keyed by identity-engine plugin names and weighted exactly as the plugin registry declares: character_consistency 0.40, prompt_accuracy 0.20, color_harmony 0.10, facial_appeal 0.10, silhouette_recognizability 0.05, child_friendliness 0.05, style_consistency 0.10. Keep it a frozen module-level literal (offline-safe); add a drift-guard unit test that constructs IdentityScorer with light=True and asserts each plugin's declared name appears in the table with an equal weight value — this catches future plugin-weight edits silently diverging from the benchmark.

    Change `BenchmarkConfig.similarity_threshold` default from 0.85 to 0.90 (G13; ROADMAP >= 90% requirement).

    Rework the `evaluate()` composite loop: iterate the canonical weight table but SKIP any dimension absent from the provider output entirely — do not zero-default missing dims and do not let their weights enter the denominator (this is the current dilution bug at L271/L290). Track matched weight sum; compute weight_coverage = matched_weight_sum / total_canonical_weight and store it on BenchmarkResult via a new optional field (default 1.0 so existing constructors stay valid). The pass gate becomes: composite_score >= config.similarity_threshold AND weight_coverage >= 1.0 — an incomplete Brand Score can never pass the production gate even if its partial average is high (A7 honesty; the Colab notebook runs full plugins so real gates have coverage 1.0). Update report() to print the coverage value when below 1.0.

    Update `MockScorerProvider` to emit the seven canonical keys (deterministic ranges in the 0.6-0.98 band, seeded RNG preserved). Update TestLoRABenchmark and TestMockScorerProvider expectations accordingly, adding the coverage/partial-dim and threshold-boundary behaviors above. Keep numpy averaging math otherwise unchanged (composite/improvement/report formatting are correct per research).

    Do NOT touch _load_baseline_images or _generate_test_images beyond what coverage reporting requires (G15 population lands in Plan 01c-01; G14 test-image supply is the CLI/notebook's job).
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_lora_training.py::TestLoRABenchmark tests/test_lora_training.py::TestMockScorerProvider -q</automated>
    <automated>python3 -m pytest tests/test_lora_training.py -q</automated>
  </verify>
  <done>
    Weight table matches the identity-engine plugin registry exactly (drift-guarded), threshold default is 0.90, missing dimensions are excluded from both numerator and denominator with explicit weight_coverage on the result, the gate demands full coverage plus >= 0.90, and all benchmark suites pass offline.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: IdentityScorerProvider adapter (G11 bridge)</name>
  <files>src/training_engine/scorer_adapter.py, src/training_engine/__init__.py, tests/test_lora_training.py</files>
  <read_first>
    @src/training_engine/benchmark.py (ScorerProvider protocol L88-111 — signature must match exactly; MockScorerProvider L118-141 as structural reference)
    @src/identity_engine/scorer.py (IdentityScorer constructor L65-67 with light flag; score_all(image, **kwargs) -> dict[str, float] L60-63 — plugin-name keys)
    @src/training_engine/__init__.py (import + __all__ export discipline L14-35)
    @.planning/phases/01c-character-training-system/01c-PATTERNS.md (scorer_adapter.py pattern assignment; Shared Patterns "Protocol seam + mock-first default")
  </read_first>
  <behavior>
    - Frozen-fixture fake scorer returning canned plugin outputs including one unknown key: adapter returns only keys present in the canonical benchmark weight table, values preserved unchanged.
    - reference_path=None path: adapter opens only the target image and delegates with reference=None.
    - Adapter satisfies the ScorerProvider protocol structurally (usable wherever LoRABenchmark expects a provider).
    - Constructing IdentityScorerProvider() with defaults succeeds offline (light mode) and scoring a tiny tmp_path image returns a dict whose keys are a subset of the canonical seven.
  </behavior>
  <action>
    Create `src/training_engine/scorer_adapter.py` defining `IdentityScorerProvider` implementing the exact `score_identity(self, image_path: Path, reference_path: Optional[Path] = None, character_id: Optional[str] = None) -> dict[str, float]` protocol shape from benchmark.py.

    Constructor accepts either an externally built IdentityScorer instance (dependency injection for tests) or a `light: bool = True` flag that constructs one internally. Light mode keeps torch-backed plugins out of the offline unit path per A7; full-plugin evaluation on Colab passes light=False.

    Implementation: open image_path with PIL (convert to RGB for safety), open reference_path the same way when provided, delegate to the wrapped scorer's score_all with the reference keyword, then filter the returned mapping to keys present in the canonical benchmark table — dropping unknown plugin names with a warnings.warn so stray future plugins cannot silently skew composites. No renaming map is needed because Task 1 aligned weights onto plugin names directly (research Pattern 1 recommended direction). character_id is accepted for protocol compliance and passed through only if the underlying scorer's signature uses it.

    Re-export `IdentityScorerProvider` from src/training_engine/__init__.py imports and __all__ per package conventions (tests import from package root).

    Add adapter tests to tests/test_lora_training.py under a new TestIdentityScorerProvider class using the frozen-fixture approach above plus one light-mode smoke test against a tmp_path dummy image. Zero torch/network imports in the test module (C-OFFLINE).
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_lora_training.py::TestIdentityScorerProvider -q</automated>
    <automated>python3 -m pytest tests/test_training_engine.py tests/test_lora_training.py -q</automated>
  </verify>
  <done>
    IdentityScorerProvider exists at package root, adapts IdentityScorer to the ScorerProvider protocol offline, filters unknown dimensions defensively, and both engine suites remain green.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Provider output → composite math | Score dicts cross into weighted-average computation |
| Image files → PIL decode | Operator-local PNG/JPEG files opened by scorer plugins |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01c-02a | Tampering | Provider dimension keys entering composite | medium | mitigate | Canonical-table filtering in adapter AND coverage-honest evaluate loop — unknown or missing dims can never inflate or silently dilute scores |
| T-01c-02b | Denial of Service | Malformed image files at PIL decode | low | accept | Single-operator local tooling; PIL raises on garbage input and callers already warn-and-skip unreadable sources |
| T-01c-SC | Tampering | Package installs | low | accept | No project-tree installs — identity_engine/Pillow/numpy already declared (C-NODEP) |
</threat_model>

<verification>
1. `python3 -m pytest tests/test_training_engine.py tests/test_lora_training.py -q` — all green offline
2. Full suite `python3 -m pytest -q` — no regressions
3. Drift-guard test proves benchmark weights equal live plugin weights (D-06 sourcing verified, not just transcribed)
</verification>

<success_criteria>
1. Real-scorer integration produces sane composites (no zero-dimension collapse — Pitfall 4 impossible by construction)
2. Threshold 0.90 locked; partial-coverage results explicitly fail rather than fake-pass
3. IdentityScorerProvider importable from package root and protocol-exact
4. All tests green without GPU/network
</success_criteria>

<output>
Create `.planning/phases/01c-character-training-system/01c-02-SUMMARY.md` when done.
</output>
