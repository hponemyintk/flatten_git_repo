# Flatten Git Repo

A Python tool to flatten a git repository into a single text file optimized for LLM consumption (Claude, Gemini, etc).

## Features

- **Recursive flattening**: Walks through entire repo and includes all text files
- **Smart exclusions**: Skip binary files, dependencies, build artifacts automatically
- **Customizable exclusions**: Exclude specific files/folders with `-e` flag
- **LLM-optimized formatting**: Clear file separators, language hints, file index
- **Respects .gitignore**: Reads and respects patterns from .gitignore
- **Safe**: Skips common unnecessary directories (`.git`, `node_modules`, `__pycache__`, etc)

## Installation

```bash
chmod +x flatten_repo.py
```

## Usage


### for flattening relgt repo
```
python ../flatten_git_repo/flatten_repo.py . -o dev-kyaw.git.repo -e arch.png c1_script docs expts LICENSE local_driver.sh notebooks pyg_wheels relbench_neigh.txt setup.sh tabpfn_icl_results.log tabpfn-v2-classifier-finetuned-zk73skhh.ckpt test_tabpfn.py wandb .ipynb_checkpoints dev-kyaw.git.repo

git diff dev-kyaw dev-kyaw-og-pass -- codebook.py encoders.py local_module.py main_node_ddp.py model.py utils.py pass_sampler.py > git_diff_dev_kyaw_vs_dev_kyaw_og_pass
```

### Basic usage
```bash
python flatten_repo.py /path/to/repo
```

This creates `flattened_repo.txt` in the current directory.

### Custom output file
```bash
python flatten_repo.py /path/to/repo -o my_repo.txt
```

### Exclude specific files/folders
```bash
python flatten_repo.py /path/to/repo -e tests/ docs/ "*.test.js" build/
```

### Combined
```bash
python flatten_repo.py /path/to/repo -o output.txt -e tests/ node_modules/extra/ .env
```

## Output Format

The flattened file includes:

1. **Header**: Repository path and file count
2. **File Index**: List of all files included
3. **File Contents**: Each file wrapped in markdown code blocks with:
   - File path
   - Detected language
   - File size
   - Content

Example:
```
================================================================================
REPOSITORY SNAPSHOT
================================================================================

Repository: /path/to/repo
Total files: 42

FILE INDEX:
--------------------------------------------------------------------------------
src/main.py
src/utils.py
tests/test_main.py
...

================================================================================

================================================================================
FILE: src/main.py
Language: python
Size: 1234 bytes
================================================================================

```python
def hello():
    print("world")
```

================================================================================
FILE: src/utils.py
...
```

## Excluded by Default

- **Directories**: `.git`, `.venv`, `venv`, `__pycache__`, `.pytest_cache`, `node_modules`, `.npm`, `.yarn`, `dist`, `build`, `.egg-info`, `.tox`, `.coverage`, `.vscode`, `.idea`, `.next`, `.nuxt`, `out`, `.cache`, `.turbo`, `tests`, `.claude`
- **Files**: `.gitignore`, `CLAUDE.md`
- **Binary files**: Images, archives, executables, compiled code
- **Hidden files**: Except `.env.example`

## Use Cases

- **LLM Code Analysis**: Send entire repo to Claude, Gemini, etc for analysis
- **Documentation**: Create a single-file reference of your codebase
- **Code Review**: Share entire context with reviewers
- **AI-assisted Refactoring**: Give models full context for better suggestions
# flatten_git_repo
