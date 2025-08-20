# Kaiten to Planka Migration Tool

A tool for migrating data from Kaiten to Planka project management systems.

## Features

- Migrate projects, boards, cards, and users from Kaiten to Planka
- Handle attachments and comments
- Idempotent migration with progress tracking
- Configurable rate limiting and retry logic
- Dry run mode for testing

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kaiten2planka.git
   cd kaiten2planka
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Configuration

1. Copy the example configuration files:
   ```bash
   cp config.yaml.template config.yaml
   cp .env.example .env
   ```

2. Edit `config.yaml` with your Kaiten and Planka instance details.
3. Add your API keys to the `.env` file.

## Usage

```bash
# Run migration
kaiten2planka migrate

# Dry run (no changes will be made)
kaiten2planka migrate --dry-run

# Force re-migrate existing data
kaiten2planka migrate --force

# Show help
kaiten2planka --help
```

## Development

1. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Run linters:
   ```bash
   black .
   isort .
   mypy .
   pylint src tests
   ```

## License

MIT
