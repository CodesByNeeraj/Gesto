# Gesto Agent Guidelines

This file defines the coding standards, naming conventions, file organisation,
and contribution workflow for Gesto. Follow these guidelines for every change,
whether you are a human contributor or an AI agent (Codex).

---

## Code Quality

Write code that is easy to read before it is clever. If a piece of logic
requires a comment to explain what it does, consider rewriting it so the code
explains itself. Comments should explain why something is done, not what is
being done.

Keep functions small and focused. A function should do one thing and do it
well. If a function is growing long, it is doing too many things and should be
split up.

No file should contain a large block of unrelated logic. If a file is getting
long, that is a signal to separate concerns into smaller modules.

Avoid magic numbers and hardcoded strings. Define them as named constants at
the top of the file or in a dedicated constants file.

---

## Naming Conventions

**Files and directories:** use kebab-case. Examples: `gesture-detector.py`,
`action-mapper.py`, `config-loader.py`.

**Functions:** use camelCase. Examples: `detectGesture`, `loadConfig`,
`mapGestureToAction`. Do not prefix functions with an underscore. There are no
private functions in this codebase by naming convention.

**Classes:** use PascalCase. Examples: `GestureDetector`, `ActionMapper`,
`ConfigLoader`.

**Variables:** use camelCase. Examples: `gestureLabel`, `confidenceScore`,
`mappedAction`.

**Constants:** use UPPER_SNAKE_CASE. Examples: `DEFAULT_CONFIDENCE_THRESHOLD`,
`COOLDOWN_PERIOD_SECONDS`, `CONFIG_FILE_PATH`.

**Gesture names:** use descriptive kebab-case labels that convey the gesture
clearly. Examples: `thumbs-up`, `open-palm`, `peace-sign`. Never use vague
names like `gesture1` or `g2`.

**Action names:** use descriptive kebab-case labels that convey the action
clearly. Examples: `open-chrome`, `media-play-pause`, `mute-microphone`.

File names and function names must convey their meaning immediately. A new
contributor reading the file tree or a function signature should understand
what it does without opening the file.

---

## File Organisation and Separation of Concerns

Each file should have a single clear responsibility. Do not mix gesture
detection logic with UI code. Do not mix configuration loading with action
execution.

Follow this structure:

```
src/
  gesture-detector.py     detects gestures from camera frames
  action-mapper.py        maps gesture labels to system actions
  action-executor.py      executes system actions on the device
  config-loader.py        reads and writes the config file
  custom-trainer.py       handles custom gesture training and saving
  camera-handler.py       manages camera access and frame capture
  ui/
    main-window.py        the main settings window
    gesture-list.py       the gesture mapping list component
    training-wizard.py    the custom gesture training flow
assets/
  models/                 built-in gesture model files
tests/
  test-gesture-detector.py
  test-action-mapper.py
  test-config-loader.py
```

If a file is growing beyond 200 lines, question whether it is doing too much
and split it.

---

## Python Coding Standards

Follow PEP 8 for all Python code. Use a formatter such as Black and a linter
such as Flake8. Do not hand-format code against these tools.

Use 4 spaces for indentation in Python files. Use 2 spaces for JSON and YAML.

Type hints are required for all function signatures.

```python
def detectGesture(frame: np.ndarray, threshold: float) -> str:
    ...
```

Do not use bare except clauses. Always catch specific exceptions.

```python
# wrong
try:
    loadConfig()
except:
    pass

# right
try:
    loadConfig()
except FileNotFoundError:
    createDefaultConfig()
```

---

## Commit Practices

Use conventional commits for every commit message. The format is:

```
type(scope): short description in imperative present tense
```

Types:

- `feat` for a new feature
- `fix` for a bug fix
- `refactor` for code changes that neither fix a bug nor add a feature
- `test` for adding or updating tests
- `docs` for documentation changes
- `chore` for maintenance tasks like dependency updates

Examples:

```
feat(gesture-detector): add open palm detection
fix(config-loader): handle missing config file on first launch
refactor(action-mapper): split mapping logic into separate function
test(gesture-detector): add edge case for low confidence score
docs(readme): add demo gif to installation section
chore(deps): update mediapipe to 0.10.5
```

Keep the subject line under 72 characters. Use the body of the commit to
explain why the change was made if it is not obvious from the subject.

Do not mix unrelated changes in a single commit. One commit should represent
one logical change.

---

## Branching and Pull Request Workflow

Never commit directly to `main`. Every change goes through a branch and a pull
request.

Name branches using the format `type/short-description`. Examples:

```
feat/thumbs-up-detection
fix/config-not-saving
refactor/separate-camera-handler
docs/update-readme-install-steps
```

One feature or fix per branch. Do not bundle unrelated changes into the same
branch.

When opening a pull request:

- Write a clear title using the same conventional commit format
- Describe what the change does and why it was made
- Note what testing was performed
- Include a screenshot or short demo GIF for any UI or gesture behaviour change
- Call out any privacy or camera permission implications
- Link any related issues

A pull request should be small enough to review in one sitting. If a pull
request is getting large, break it into smaller ones.

---

## Testing

Write a test for every new behaviour. Tests live in `tests/` and mirror the
path of the file they cover.

Name test files after the module they test. Examples: `test-gesture-detector.py`,
`test-action-mapper.py`.

Use descriptive test function names that read like a sentence describing the
expected behaviour.

```python
def test_gestureIsIgnoredWhenConfidenceBelowThreshold():
    ...

def test_configSavesCorrectlyAfterMappingIsAdded():
    ...
```

Cover these cases for every gesture-related function:

- The happy path where the gesture is detected correctly
- Low confidence input that should be ignored
- Invalid or empty camera frame input
- Edge cases specific to the gesture being tested

Run all tests before opening a pull request.

---

## CI Compatibility

All tests must pass in a headless environment with no camera, no display, and
no local file paths. The CI pipeline runs on a clean machine that has none of
your local files or hardware. Tests that pass locally but fail in CI are not
acceptable.

**Never hardcode local file paths in tests.**

```python
# wrong
frame = loadTestFrame("/Users/Desktop/Gesto/assets/thumbs-up.jpg")

# right
frame = loadTestFrame(Path(__file__).parent / "fixtures" / "thumbs-up.jpg")
```

**Always mock hardware access.**
Tests must never try to open a real camera. The CI environment has no camera.
Use unittest.mock to simulate camera input instead.

```python
from unittest.mock import patch
import numpy as np

def test_gestureDetectorHandlesEmptyFrame():
    with patch("cv2.VideoCapture") as mockCamera:
        mockCamera.return_value.read.return_value = (True, np.zeros((480, 640, 3)))
        result = detectGesture(frame=np.zeros((480, 640, 3)), threshold=0.8)
        assert result is None
```

**Commit all test fixtures to the repo.**
Any sample images, landmark data, or other files that tests depend on must be
committed under `tests/fixtures/` so the CI environment has access to them.
Never reference a file that only exists on your local machine.

If a test requires a fixture file that is too large to commit, mock the data
instead of using the real file.

---

## Test Driven Development

Gesto follows test driven development. This means you write the test before
you write the function. No new function should exist without a test that was
written first.

The workflow for every new behaviour is:

**Step 1. Write a failing test.**
Before writing any implementation code, write a test that describes the
behaviour you want. Run it. It must fail. A test that passes before the
implementation exists means the test is not testing anything real.

```python
def test_gestureDetectorReturnsThumbs_upWhenThumbnailIsRaised():
    frame = loadTestFrame("thumbs-up-sample.jpg")
    result = detectGesture(frame, threshold=0.8)
    assert result == "thumbs-up"
```

Run the test. It fails because `detectGesture` does not exist yet. That is
correct. Move to step 2.

**Step 2. Write the minimum code to make the test pass.**
Do not write more code than is needed to make the failing test pass. Resist
the urge to build ahead. Write exactly what the test requires and nothing more.

**Step 3. Run the test again.**
It must pass now. If it does not, fix the implementation until it does. Do not
move on until the test is green.

**Step 4. Refactor.**
Now that the test is passing, clean up the implementation if needed. Improve
the naming, simplify the logic, remove duplication. Run the tests again after
every change to make sure nothing broke.

**Step 5. Repeat.**
Write the next failing test for the next behaviour and go through the cycle
again.

This cycle is: red, green, refactor. Red means the test fails. Green means
the test passes. Refactor means you clean up without breaking anything.

Never skip the red step. If you write the implementation before the test you
will write tests that are shaped around your implementation rather than around
the required behaviour. Those tests do not protect you from bugs.

Every pull request must show that tests were written before the implementation.
The commit history should reflect this. A commit adding a test should appear
before the commit adding the function it tests.

```
test(gesture-detector): add failing test for thumbs-up detection
feat(gesture-detector): implement thumbs-up detection to pass test
refactor(gesture-detector): simplify confidence threshold check
```

If you are fixing a bug, write a test that reproduces the bug first. The test
must fail against the buggy code. Then fix the bug. The test must now pass.
This ensures the bug can never silently return.

---

## Privacy and Camera Handling

No video frames, gesture data, hand landmarks, or any camera input must ever
be sent to an external server or third party service. All processing happens
locally on the device.

Any function that accesses the camera must release it cleanly when it is no
longer needed. Do not leave the camera open in the background when Gesto is
not actively detecting.

Document any camera or microphone permission implications clearly in pull
request descriptions and in code comments where relevant.