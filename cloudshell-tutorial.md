# Perra (Persona Radar)

<div align="center">
  <img src="https://raw.githubusercontent.com/codevcn/perra/main/static/perra.png" height="220" alt="Perra logo"/>
</div>

**Perra** collects a dossier on a person **by username or identifier**, checking for accounts across thousands of sites and gathering public profile data without requiring API keys.

## Installation

Install from source in Cloud Shell:

```bash
./utils/cloudshell_install.sh
```

Verify the install:

```bash
perra --version
```

## Usage examples

Run a basic search for a username. By default Perra checks the **500 highest-ranked sites by traffic** — pass `-a` to scan the full database.

```bash
perra johndoe
```

Search several usernames at once:

```bash
perra user1 user2 user3
```

Narrow the run to sites related to cryptocurrency via the `crypto` tag:

```bash
perra vitalik.eth --tags crypto
```

Generate reports in HTML, PDF, and XMind 8 formats:

```bash
perra johndoe --html
perra johndoe --pdf
perra johndoe --xmind
```

Download a generated report from Cloud Shell to your local machine:

```bash
cloudshell download reports/report_johndoe.pdf
```

Check for CLI updates manually:

```bash
perra update --check
```

Tune reliability on flaky networks — raise the timeout and retry failed checks:

```bash
perra johndoe --timeout 60 --retries 2
```

For the full list of options run `perra --help`.
