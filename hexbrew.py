import yaml
import os
import hashlib
import tarfile
from pathlib import Path

class BrewPackager:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.name = self.config['name']
        self.version = self.config['version']
        self.files_dir = Path(self.config['files_dir'])
        self.output_dir = Path(self.config['output_dir'])
        self.codesign = self.config.get('codesign', False)
        self.download_url = self.config['download_url']
        self.commands = self.config.get('commands', [])

    def create_tarball(self):
        """Create tar.gz archive of files"""
        tarball_path = self.output_dir / f"{self.name}-{self.version}.tar.gz"
        with tarfile.open(tarball_path, "w:gz") as tar:
            tar.add(self.files_dir, arcname=self.name)
        return tarball_path
    
    def calculate_sha256(self, file_path):
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def generate_formula(self, tarball_path, sha256):
        """Generate Ruby formula file for brew tap with embedded commands"""
        formula = f"""class {self.name.capitalize()} < Formula
    desc "{self.config['description']}"
    homepage "{self.config['homepage']}"
    """
        #Add custom download URL if enabled
        if self.download_url:
            formula += f"""url "{self.download_url}"
    """
        else:
            formula += f"""url https://github.com/{self.config['github_repo']}/releases/download/v{self.version}/{tarball_path.name}"
    """
            
        formula += f"""sha256 "{sha256}"
    version "{self.version}"

    def install
        bin.install Dir["*"]
    """

        # Add codesigning if enabled
        if self.codesign:
            formula += """    Dir["#{bin}/*"].each do |f|
        system "codesign", "--force", "--sign", "-", f if File.file?(f)
        end
    """

        # Add commands
        if self.commands:
            formula += "\n".join(f'    system "{cmd}"' for cmd in self.commands)
            formula += "\n"

        formula += "  end\n"

        # Add caveats
        caveat = self.config.get("caveat")
        if caveat:
            formula += f"""
    def caveats
        <<~EOS
        {caveat.strip()}
        EOS
    end
    """

        formula += "end\n"

        formula_path = self.output_dir / "Formula" / f"{self.name}.rb"
        os.makedirs(formula_path.parent, exist_ok=True)
        with open(formula_path, "w") as f:
            f.write(formula)
        return formula_path
    
    def print_github_commands(self):
        """Print commands for GitHub setup"""
        repo = self.config['github_repo']
        print(f"\nCreated release v{self.version} and upload {self.name}-{self.version}.tar.gz\n\n")
        print("To push to GitHub, run:")
        print("  cd", self.output_dir)
        print("  git init")
        print("  git add .")
        print('  git commit -m "Initial brew tap commit"')
        print("  git branch -M main")
        print(f"  git remote add origin https://github.com/{repo}.git")
        print("  git push -u origin main\n\n")
        print("To install with brew:")
        print(f"  brew tap {repo}")
        print(f"  brew install {self.name}")


    def build(self):
        """Build complete brew tap package"""
        os.makedirs(self.output_dir, exist_ok=True)
        tarball_path = self.create_tarball()
        sha256 = self.calculate_sha256(tarball_path)
        formula_path = self.generate_formula(tarball_path, sha256)
        self.print_github_commands()

if __name__ == "__main__":
    packager = BrewPackager("config.yaml")
    result = packager.build()
