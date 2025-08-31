# automatic-beer-goggles

A minimal repository containing basic project documentation.

**ALWAYS follow these instructions first and only fallback to additional search and context gathering if the information in these instructions is incomplete or found to be in error.**

## Repository Overview

This repository currently contains minimal content:
- `README.md` - Basic project documentation
- `.github/copilot-instructions.md` - These instructions

## Working Effectively

### Repository Navigation
- View repository structure: `ls -la`
- View all files (excluding .git): `find . -type f ! -path "./.git/*"`
- Read the README: `cat README.md`

### Git Operations
- Check repository status: `git status`
- View recent commits: `git log --oneline -10`
- View current branch: `git branch --show-current`
- View all branches: `git branch -a`

### Development Workflow
**IMPORTANT**: This repository currently contains no source code, build systems, or dependencies.

- No build commands are available (no package.json, Makefile, or other build configuration)
- No test commands are available (no test framework configured)
- No installation steps required (no dependencies)
- No compilation or runtime environment needed

### Validation Steps
When making changes to this repository:
1. Verify files exist: `ls -la`
2. Check git status: `git status`
3. Validate file contents: `cat [filename]`
4. Ensure proper markdown syntax for .md files

## Repository Structure

```
.
├── .git/                    # Git repository data
├── .github/                 # GitHub configuration
│   └── copilot-instructions.md
└── README.md               # Project documentation
```

## Common Tasks

### Adding New Files
- Create files with appropriate names and extensions
- Update README.md if the new files represent significant functionality
- Commit changes with descriptive messages

### Documentation
- README.md follows basic markdown format
- Keep documentation concise and accurate
- Update these instructions if significant project structure changes occur

## Expected Command Outputs

### Repository Root Listing
```bash
$ ls -la
total 16
drwxr-xr-x 3 runner docker 4096 [date] .
drwxr-xr-x 3 runner docker 4096 [date] ..
drwxr-xr-x 7 runner docker 4096 [date] .git
drwxr-xr-x 2 runner docker 4096 [date] .github
-rw-r--r-- 1 runner docker   43 [date] README.md
```

### README Content
```bash
$ cat README.md
# automatic-beer-goggles
Just like we said
```

### File Discovery
```bash
$ find . -type f ! -path "./.git/*"
./.github/copilot-instructions.md
./README.md
```

## Important Notes

- **No Build Required**: This repository contains no buildable code
- **No Dependencies**: No package managers or dependency installation needed
- **No Testing Framework**: No automated tests to run
- **No Runtime Environment**: No application to start or serve
- **Documentation Focus**: Changes should focus on documentation and project structure

## Future Development

When source code is added to this repository:
1. Update these instructions with build commands
2. Add dependency installation steps
3. Include testing procedures
4. Document any new development workflows
5. Add timeout warnings for any commands that may take longer than 2 minutes

## Validation

To validate these instructions work correctly:
1. Clone the repository fresh
2. Run `ls -la` to see repository structure
3. Run `cat README.md` to view documentation
4. Run `git status` to check repository state
5. Verify all commands listed above execute successfully