# automatic-beer-goggles

Documentation repository for Automatic Beer Goggles - a Python CLI tool for automated video creation for social media platforms.

**ALWAYS follow these instructions first and only fallback to additional search and context gathering if the information in these instructions is incomplete or found to be in error.**

## Repository Overview

This repository contains documentation for the Automatic Beer Goggles project:
- `README.md` - Project overview and quick links
- `docs/` - Complete documentation site with GitHub Pages deployment
- `.github/` - GitHub configuration including workflows and these instructions

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
**IMPORTANT**: This repository contains documentation for a Python CLI tool project.

- The docs/ folder contains a complete documentation site deployed via GitHub Pages
- Jekyll is used for site generation (see docs/_config.yml)
- GitHub Actions workflow (.github/workflows/pages.yml) handles automatic deployment
- The main documentation files are docs/index.html and docs/README.md
- All documentation should be kept synchronized and consistent

### Validation Steps
When making changes to this repository:
1. Verify files exist: `ls -la`
2. Check git status: `git status`
3. Validate file contents: `cat [filename]`
4. Ensure proper markdown syntax for .md files
5. Check HTML syntax in docs/index.html
6. Verify links work correctly in documentation
7. Ensure consistency between docs/README.md and docs/index.html

## Repository Structure

```
.
├── .git/                    # Git repository data
├── .github/                 # GitHub configuration
│   ├── copilot-instructions.md # These instructions
│   └── workflows/
│       └── pages.yml        # GitHub Pages deployment workflow
├── docs/                    # Documentation site
│   ├── .nojekyll           # GitHub Pages configuration
│   ├── _config.yml         # Jekyll configuration
│   ├── index.html          # Main documentation site
│   └── README.md           # Detailed documentation
└── README.md               # Project overview
```

## Common Tasks

### Updating Documentation
- Edit docs/README.md for detailed documentation changes
- Edit docs/index.html for website presentation changes
- Ensure consistency between both documentation files
- Update platform specifications, CLI commands, and examples as needed
- Commit changes with descriptive messages

### GitHub Pages Deployment
- Changes to docs/ folder automatically trigger deployment via GitHub Actions
- The site is available at: https://drkv8r.github.io/automatic-beer-goggles
- Jekyll configuration is in docs/_config.yml

### Documentation
- Main README.md provides project overview and links to documentation site
- docs/README.md contains comprehensive documentation
- docs/index.html provides user-friendly web interface
- Keep all documentation synchronized and accurate

## Expected Command Outputs

### Repository Root Listing
```bash
$ ls -la
total 20
drwxr-xr-x 5 runner docker 4096 [date] .
drwxr-xr-x 3 runner docker 4096 [date] ..
drwxr-xr-x 7 runner docker 4096 [date] .git
drwxr-xr-x 3 runner docker 4096 [date] .github
-rw-r--r-- 1 runner docker 1498 [date] README.md
drwxr-xr-x 2 runner docker 4096 [date] docs
```

### README Content
```bash
$ cat README.md
# automatic-beer-goggles
Just like we said

🍺 **Automated mastered audio-image video creation for social media platforms**

An advanced Python system that automates the creation of videos combining static PNG images with mastered audio files, producing platform-optimized videos for broad social video and audio distribution.

**📚 [Visit our documentation site](https://drkv8r.github.io/automatic-beer-goggles) for detailed guides, examples, and setup instructions.**
```

### File Discovery
```bash
$ find . -type f ! -path "./.git/*"
./README.md
./docs/.nojekyll
./docs/README.md
./docs/_config.yml
./docs/index.html
./.github/copilot-instructions.md
./.github/workflows/pages.yml
```

## Important Notes

- **Documentation Focus**: This repository contains documentation for the Automatic Beer Goggles Python CLI tool
- **GitHub Pages**: Documentation site is automatically deployed to https://drkv8r.github.io/automatic-beer-goggles
- **Jekyll Configuration**: Site generation handled by Jekyll (docs/_config.yml)
- **Workflow Automation**: GitHub Actions automatically deploys changes to docs/ folder
- **Consistency Required**: Keep docs/README.md and docs/index.html synchronized

## Future Development

When the actual Python CLI tool source code is added to this repository:
1. Update these instructions with build commands and testing procedures
2. Add dependency installation steps (requirements.txt)
3. Include development environment setup
4. Document any new development workflows
5. Add timeout warnings for commands that may take longer than 2 minutes
6. Consider separating documentation and source code into different repositories

## Validation

To validate these instructions work correctly:
1. Clone the repository fresh
2. Run `ls -la` to see repository structure  
3. Run `cat README.md` to view documentation
4. Run `git status` to check repository state
5. Check docs/ folder: `ls -la docs/`
6. Verify GitHub Pages site loads: https://drkv8r.github.io/automatic-beer-goggles
7. Ensure all commands listed above execute successfully