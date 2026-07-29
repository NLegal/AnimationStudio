---
phase: 01b-character-asset-production
plan: 03
type: execute
wave: 1
depends_on: []
files_modified:
  - src/generation_engine/workflows/reference_sheet.json
  - src/generation_engine/workflows/expression.json
  - src/generation_engine/workflows/pose.json
  - src/generation_engine/workflows/outfit.json
  - src/generation_engine/comfy_backend.py
  - tests/test_generation_engine.py
autonomous: true
requirements:
  - CHAR-02
  - CHAR-03
  - CHAR-04
  - CHAR-05
user_setup:
  - service: ComfyUI
    why: "Production image generation engine — all Phase 1b generation runs through ComfyUI + Flux"
    env_vars: []
    dashboard_config:
      - task: "Install ComfyUI (git clone https://github.com/comfyanonymous/ComfyUI)"
      - task: "Download Flux model weights (flux1-dev.safetensors or Flux.2 Klein) into ComfyUI/models/checkpoints/"
      - task: "Start ComfyUI server: python main.py --listen 127.0.0.1 --port 8188"
must_haves:
  truths:
    - ComfyUIBackend._load_workflow_template(asset_type="expression") loads the expression workflow JSON file
    - ComfyUI + Flux is the primary production path per D-01 (SDXL secondary); ComfyUI is the heart of the studio per D-02
    - ComfyUIBackend._load_workflow_template(asset_type="unknown") falls back to _DEFAULT_WORKFLOW_TEMPLATE
    - Reference sheet workflow uses cfg=3.5, steps=25, empty negative prompt (Flux-optimized)
    - Expression workflow uses cfg=3.5, steps=25, portrait dimensions (1024x1024)
    - Pose workflow uses cfg=3.5, steps=25, full-body dimensions (768x1344)
    - Outfit workflow uses cfg=3.5, steps=25, full-body dimensions (768x1344)
    - All workflow JSON files are API-format (numeric string keys, class_type + inputs only)
  artifacts:
    - src/generation_engine/workflows/reference_sheet.json
    - src/generation_engine/workflows/expression.json
    - src/generation_engine/workflows/pose.json
    - src/generation_engine/workflows/outfit.json
    - src/generation_engine/comfy_backend.py (updated _load_workflow_template, updated _build_workflow)
  key_links:
    - Workflow JSON node IDs (3=KSampler, 6=CLIPTextEncode positive, 7=CLIPTextEncode negative) must match what _build_workflow() expects
    - Flux cfg=3.5 (not SDXL cfg=7.0) — see Research Pitfall 2
    - Flux negative prompt should be empty string (Flux ignores negative prompts)
    - Workflow files must be API-format (exported via ComfyUI "Save (API Format)"), not GUI format
---

<objective>
Create Flux-optimized ComfyUI API-format workflow templates for all four asset types (reference sheet, expression, pose, outfit) and update the ComfyUIBackend to load type-specific workflows with correct Flux sampling parameters. Per D-01, ComfyUI + Flux is the primary production path (SDXL is secondary). Per D-02, ComfyUI is the heart of the studio — all production generation runs through ComfyUI workflows; Python/diffusers adapters remain supported but are not primary for Phase 1b.

Purpose: Enable the production pipeline to generate character-consistent images through ComfyUI + Flux by providing the workflow definitions that the ComfyUIBackend submits to the server.
Output: Four API-format workflow JSON files and updated ComfyUIBackend with type-aware template loading.
</objective>

<execution_context>
@/root/.config/opencode/gsd-core/workflows/execute-plan.md
@/root/.config/opencode/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01b-character-asset-production/01b-CONTEXT.md
@.planning/phases/01b-character-asset-production/01b-RESEARCH.md

# Source files
@src/generation_engine/comfy_backend.py
@src/generation_engine/base.py
@src/generation_engine/__init__.py
@src/prompt_builder/templates.py
@Universe/Characters/Lily Bunny/bio.md
@Universe/ColorPalette/brand-palette.json
@tests/test_generation_engine.py
@tests/conftest.py
</context>

<tasks>

<task type="auto">
  <name>Create Flux API-format workflow JSON templates for all 4 asset types</name>
  <files>
    src/generation_engine/workflows/reference_sheet.json,
    src/generation_engine/workflows/expression.json,
    src/generation_engine/workflows/pose.json,
    src/generation_engine/workflows/outfit.json
  </files>
  <read_first>
    @src/generation_engine/comfy_backend.py (lines 26-48 — _DEFAULT_WORKFLOW_TEMPLATE, lines 237-286 — _build_workflow and _load_workflow_template),
    @.planning/phases/01b-character-asset-production/01b-RESEARCH.md (lines 246-269 — Pattern 2: ComfyUI Workflow-as-Template, lines 269-276 — Anti-Patterns for workflow JSON, lines 331-335 — Pitfall 2 Flux params),
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-01, D-02, D-03: Cloud APIs are optional adapters only — never mandatory dependencies),
    @src/prompt_builder/templates.py (lines 69-104 — template methods to understand prompt structure for each asset type)
  </read_first>
  <action>
    Create the directory `src/generation_engine/workflows/` if it doesn't exist.

    Create four API-format workflow JSON files. Each must be valid ComfyUI API-format (numeric string keys, ONLY `class_type` and `inputs` fields — NO position, color, or size metadata per Anti-Pattern Pitfall 1).

    **Common Flux sampling parameters** (per RESEARCH.md Pitfall 2):
    - Flux.1 Dev: cfg=3.5, steps=25, sampler_name="euler", scheduler="normal"
    - Flux negative prompt: empty string (Flux ignores negatives — leave CLIPTextEncode node 7 with empty text)
    - Width/Height: injected at runtime by _build_workflow(), but set sensible defaults
    - Model checkpoint: "flux1-dev.safetensors" (parameterizable — the backend also accepts external model paths)

    **reference_sheet.json** — Multi-angle reference sheet generation
    - KSampler: seed=[placeholder], steps=25, cfg=3.5, sampler_name="euler", scheduler="normal", denoise=1.0
    - CheckpointLoaderSimple: ckpt_name="flux1-dev.safetensors"
    - EmptyLatentImage: width=1024, height=1024, batch_size=1
    - CLIPTextEncode (positive — node 6): text="" (injected by backend)
    - CLIPTextEncode (negative — node 7): text="" (Flux — leave empty)
    - VAEDecode: samples from KSampler, vae from CheckpointLoader
    - SaveImage: filename_prefix="lily-reference"

    **expression.json** — Expression portrait generation
    - Same structure as reference sheet but:
    - EmptyLatentImage: width=1024, height=1024 (portrait/square)
    - SaveImage: filename_prefix="lily-expression"

    **pose.json** — Full-body pose generation
    - EmptyLatentImage: width=768, height=1344 (portrait full-body ratio ~9:16)
    - SaveImage: filename_prefix="lily-pose"

    **outfit.json** — Outfit/wardrobe variant generation
    - EmptyLatentImage: width=768, height=1344 (portrait full-body ratio ~9:16)
    - SaveImage: filename_prefix="lily-outfit"

    **File format requirements:**
    - JSON extension, not .jsonc or .txt
    - Valid JSON with double quotes (no trailing commas)
    - Node IDs MUST be string keys ("3", "4", "5", "6", "7", "8", "9")
    - Node connections use the `["node_id", output_index]` array format
    - Each file has EXACTLY these 7 nodes with the correct class types:
      - "3": KSampler
      - "4": CheckpointLoaderSimple
      - "5": EmptyLatentImage
      - "6": CLIPTextEncode (positive — text injected)
      - "7": CLIPTextEncode (negative — empty for Flux)
      - "8": VAEDecode
      - "9": SaveImage

    **IMPORTANT:** The node IDs must match what `_build_workflow()` in comfy_backend.py expects (it injects into nodes "3", "6", "7", "5" by class_type checking). See lines 250-266.

    **Validation:** After creating all 4 files, run:
    ```bash
    python -c "import json; json.load(open('src/generation_engine/workflows/reference_sheet.json')); json.load(open('src/generation_engine/workflows/expression.json')); json.load(open('src/generation_engine/workflows/pose.json')); json.load(open('src/generation_engine/workflows/outfit.json')); print('All valid')"
    ```

    Do NOT add any additional nodes (ControlNet, IP-Adapter, LoRA loaders) — those come in Phase 1c. Pure Flux generation only.

    **Per D-03:** These workflows run through local ComfyUI only. Cloud APIs (fal.ai, Replicate, etc.) remain as optional Tier 3 adapters in the Generation Engine architecture — never mandatory dependencies. No cloud API configurations appear in these workflow files.
  </action>
  <verify>
    <automated>python -c "import json; [json.load(open(f'src/generation_engine/workflows/{f}.json')) for f in ['reference_sheet','expression','pose','outfit']]; print('All 4 workflow files are valid JSON')"</automated>
    <automated>pytest tests/test_generation_engine.py::TestComfyUIWorkflowLoading -x --timeout=15</automated>
  </verify>
  <done>
    - 4 API-format workflow JSON files exist in src/generation_engine/workflows/
    - Each contains exactly 7 nodes with correct class types
    - Flux-optimized params (cfg=3.5, empty negative, steps=25) in all files
    - Correct dimensions per asset type (1024x1024 for ref/expression, 768x1344 for pose/outfit)
    - All files pass JSON validation
    - Test template loading test passes
  </done>
  <acceptance_criteria>
    - 4 .json files exist in src/generation_engine/workflows/
    - Each is valid JSON with numeric string keys (not GUI format)
    - Each has cfg=3.5 in node "3" KSampler inputs
    - Each has node "7" with empty text input (negative prompt)
    - reference_sheet and expression have 1024x1024 EmptyLatentImage
    - pose and outfit have 768x1344 EmptyLatentImage
  </acceptance_criteria>
</task>

<task type="auto" tdd="true">
  <name>Update ComfyUIBackend for type-specific workflow loading with Flux-optimized injection</name>
  <files>
    src/generation_engine/comfy_backend.py,
    tests/test_generation_engine.py
  </files>
  <read_first>
    @src/generation_engine/comfy_backend.py (full file — lines 1-286),
    @src/generation_engine/workflows/reference_sheet.json,
    @.planning/phases/01b-character-asset-production/01b-RESEARCH.md (lines 246-269 — Pattern 2, lines 272-276 — Anti-Patterns, lines 331-335 — Pitfall 2)
  </read_first>
  <behavior>
    - Test 1: ComfyUIBackend._load_workflow_template("expression") returns a dict with node "3" class_type="KSampler"
    - Test 2: ComfyUIBackend._load_workflow_template("reference_sheet") returns node "5" inputs width=1024
    - Test 3: ComfyUIBackend._load_workflow_template("pose") returns node "5" inputs width=768, height=1344
    - Test 4: ComfyUIBackend._load_workflow_template("nonexistent_type") returns the _DEFAULT_WORKFLOW_TEMPLATE fallback
    - Test 5: ComfyUIBackend._build_workflow() correctly injects prompt into node "6" text regardless of which template is loaded
  </behavior>
  <action>
    Update `ComfyUIBackend` in comfy_backend.py:

    **1. Add constant for workflow directory:**
    ```python
    _WORKFLOW_DIR = Path(__file__).parent / "workflows"
    ```

    **2. Update `_load_workflow_template()` to accept an `asset_type` parameter:**
    Change signature from `_load_workflow_template(self) -> dict` to `_load_workflow_template(self, asset_type: str = "") -> dict`.

    Logic:
    ```python
    def _load_workflow_template(self, asset_type: str = "") -> dict:
        """Load the workflow template for the given asset type.
        
        Looks for {asset_type}.json in the workflows directory.
        Falls back to _DEFAULT_WORKFLOW_TEMPLATE if not found.
        """
        import copy
        
        if asset_type:
            template_path = _WORKFLOW_DIR / f"{asset_type}.json"
            if template_path.exists():
                with open(template_path) as f:
                    return json.load(f)
            logger.warning(
                "Workflow template '%s' not found at %s. "
                "Falling back to default template.",
                asset_type, template_path,
            )
        
        # Fall back to single template file
        template_path = Path(__file__).parent / "comfy_workflow.json"
        if template_path.exists():
            with open(template_path) as f:
                return json.load(f)
        
        # Fall back to built-in template
        return copy.deepcopy(_DEFAULT_WORKFLOW_TEMPLATE)
    ```

    **3. Update `_build_workflow()` to pass asset_type:**
    Change signature from `_build_workflow(self, input: GenerationInput) -> dict` to `_build_workflow(self, input: GenerationInput, asset_type: str = "") -> dict`.

    Pass `asset_type` to `_load_workflow_template()`:
    ```python
    workflow = self._load_workflow_template(asset_type)
    ```

    **4. Update `_generate_rest()` and `_generate_pycomfy()`** to accept and pass `asset_type`:

    Both methods call `self._build_workflow(input)` — update to `self._build_workflow(input, asset_type)`.

    Add `asset_type: str = ""` parameter to both methods.

    **5. Keep the existing `_DEFAULT_WORKFLOW_TEMPLATE`** as the final fallback.

    **6. Add test class `TestComfyUIWorkflowLoading` in test_generation_engine.py:**
    - `test_load_expression_workflow`: Load expression template, verify node "3" has cfg=3.5, verify node "7" has empty text
    - `test_load_reference_sheet_workflow`: Load reference_sheet template, verify 1024x1024 dimensions
    - `test_load_pose_workflow`: Load pose template, verify 768x1344 dimensions
    - `test_load_fallback_on_unknown_type`: Load nonexistent type, verify returns default template (which has cfg=7.0 — SDXL default — confirming fallback)
    - `test_prompt_injection_into_loaded_workflow`: Build workflow with GenerationInput(prompt="test prompt"), verify node "6" has text="test prompt"

    **Important:** The test does NOT require a running ComfyUI server. It only validates template loading and prompt injection — both are local operations.
  </action>
  <verify>
    <automated>pytest tests/test_generation_engine.py::TestComfyUIWorkflowLoading --timeout=30 -x -v</automated>
  </verify>
  <done>
    - ComfyUIBackend._load_workflow_template("expression") loads the dedicated expression workflow JSON
    - ComfyUIBackend._load_workflow_template("nonexistent") falls back to _DEFAULT_WORKFLOW_TEMPLATE
    - ComfyUIBackend._build_workflow() correctly injects prompt into loaded type-specific templates
    - All 4 type-specific workflows load correctly
    - All 5 tests pass
  </done>
  <acceptance_criteria>
    - _load_workflow_template accepts asset_type parameter
    - Type-specific files loaded from src/generation_engine/workflows/{type}.json
    - Fallback chain: type-specific → comfy_workflow.json → _DEFAULT_WORKFLOW_TEMPLATE
    - Prompt injection into node "6" works regardless of template source
  </acceptance_criteria>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Pipeline code → Workflow JSON files | Local file reads from version-controlled workflow templates |
| ComfyUIBackend → ComfyUI REST API | HTTP localhost connection to port 8188 |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01b-07 | Tampering | Workflow JSON files | low | accept | Workflow files are version-controlled and read-only at runtime. No user-submitted workflows are loaded — only predefined templates from the workflows/ directory. |
| T-01b-08 | Tampering | ComfyUI REST API /prompt | medium | mitigate | ComfyUI defaults to binding on 127.0.0.1:8188 (localhost-only). The backend URL is hardcoded to localhost. If remote exposure is needed, require reverse proxy with API key auth (out of scope for Phase 1b). |
| T-01b-09 | Spoofing | ComfyUI model checkpoint name | low | accept | The checkpoint name ("flux1-dev.safetensors") is hardcoded in workflow JSON. If the actual file has a different name, generation fails with a clear error from ComfyUI. Users can modify the workflow JSON to match their installed model. |
| T-01b-SC | Tampering | No new pip package installs | low | accept | This plan uses only stdlib json, pathlib, and existing dependencies. |
</threat_model>

<verification>
1. `python -c "import json; json.load(open('src/generation_engine/workflows/reference_sheet.json'))"` — valid JSON
2. `pytest tests/test_generation_engine.py::TestComfyUIWorkflowLoading -x --timeout=30 -v` — workflow loading tests pass
3. `pytest tests/ --timeout=60 -x` — full test suite green
</verification>

<success_criteria>
1. Four Flux-optimized API-format workflow JSON files created
2. ComfyUIBackend loads type-specific workflows by asset_type
3. Fallback chain preserves backward compatibility
4. All workflow tests pass
</success_criteria>

<output>
Create `.planning/phases/01b-character-asset-production/01b-03-SUMMARY.md` when done.
</output>
