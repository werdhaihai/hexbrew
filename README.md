# hexbrew
HexBrew reads a YAML configuration file and outputs a formula and commands to create a homebrew tap

![hexbrew2](https://github.com/user-attachments/assets/9324da73-d9fd-49c9-ae41-09990dd17e53)

## Requirements
- Python 3
- PyYAML (install with: pip install pyyaml)

## Usage
- Create a config.yaml file (see example below).
- Place your payload files in the `files/` directory
- Run the tool:

```bash
python hexbrew.py
```
- Follow the printed GitHub commands to set up your Homebrew tap.

## Example config.yaml

```yaml
name: poseidon
version: 1.33.7
description: Command and Control
homepage: https://github.com/werdhaihai/
github_repo: werdhaihai/maliciousformula
files_dir: ./files
output_dir: ./dist
codesign: true
commands: 
caveat: |
  To finish installation, add the following line to .zshrc or .bashrc  
    source #{bin}/completion.sh
  Then reopen your terminal app 
```
