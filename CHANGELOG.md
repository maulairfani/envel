# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Responsive mobile layout for the web app: a slide-in sidebar drawer with a
  hamburger top bar on small screens, stacked page headers, and tool-call JSON
  that scrolls within a capped height instead of stretching the chat (#4).
- Open-source project scaffolding: `LICENSE` (AGPL-3.0), `CONTRIBUTING.md`
  (with CLA terms), issue & pull request templates, `.editorconfig`, and this
  changelog.

### Changed

- Reworked the README around AI-first positioning (budget from your own MCP
  client; the bundled agent + web app as an included option) and synced
  `CLAUDE.md` to the actual architecture.
- The agent now defaults to replying in English (was Bahasa Indonesia); all
  docs, code comments, and UI strings are now English.

### Fixed

- Web: protected pages returned HTTP 500 behind the reverse proxy because the
  login redirect used a relative URL; it is now built from the forwarded
  host/proto headers (#5).

[Unreleased]: https://github.com/maulairfani/envel/commits/main
