# OpenWrt golang latest version

## How to use?

After the `./scripts/feeds install -a` operation is completed, execute the following command:

```shell
rm -rf feeds/packages/lang/golang
git clone https://github.com/sbwml/packages_lang_golang -b 24.x feeds/packages/lang/golang
```

## Automated Updates

This repository now uses GitHub Actions for automated Golang version updates, replacing the previous manual Gitea-based process.

### Features

- **Automatic daily checks** for new Go releases
- **Automated hash verification** of source packages  
- **Pull Request creation** for version updates
- **Manual trigger support** for immediate updates

### Documentation

For detailed information about the automation system, see [docs/AUTOMATION.md](docs/AUTOMATION.md).

### Quick Manual Update

```bash
# Install dependencies
pip install requests beautifulsoup4 lxml

# Update to latest version
python3 scripts/update-golang.py

# Update to specific version
python3 scripts/update-golang.py 1.24.6
```
