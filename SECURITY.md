# Security Policy

## Supported Versions

Only the latest version on the `main` branch is supported with security updates.

## Reporting a Vulnerability

If you discover a security vulnerability in the data pipeline or API client, please do not open a public issue. Open a [GitHub Security Advisory](https://github.com/thedatavigilante/UI_INDEX/security/advisories/new) or contact the maintainer via the contact methods listed in [SUPPORT.md](SUPPORT.md). We will respond within 48 hours and coordinate a fix and disclosure timeline.

## Data Integrity

All data files include `_metadata` provenance blocks documenting source, timestamp, and generation script. If you suspect data tampering, verify against the original sources (BLS, FEC, Census, HUD) before citing. The CI/CD validation workflow runs on every push to verify file integrity.

## Dependency Security

This project uses Dependabot for automated dependency scanning. See [.github/dependabot.yml](.github/dependabot.yml) for configuration.
