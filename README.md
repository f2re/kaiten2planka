# Kaiten to Planka Migration Tool

This tool helps migrate data from Kaiten to Planka, including boards, cards, users, and other entities.

## Prerequisites

1. Python 3.7 or higher
2. A virtual environment (recommended)

## Setup

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example configuration files:
   ```bash
   cp config.yaml.template config.yaml
   cp .env.example .env
   ```

2. Update `config.yaml` with your Kaiten and Planka API URLs

3. Update `.env` with your API keys:
   - `KAITEN_API_KEY`: Your Kaiten API key
   - `PLANKA_API_KEY`: Your Planka API key

## Usage

Before running the migration, test your connections:
```bash
source venv/bin/activate
python utils.py test-both
```

Run the migration script:
```bash
source venv/bin/activate
python main.py
```

## Testing

Run all tests:
```bash
source venv/bin/activate
python run_tests.py
```

Run specific test files:
```bash
source venv/bin/activate
python -m unittest tests.test_kaiten_client
python -m unittest tests.test_planka_client
python -m unittest tests.test_migration
```

All tests are currently passing, verifying that:
- Kaiten client has all required methods for data retrieval
- Planka client has all required methods for data creation
- Migration module has all required methods for the migration process

## What Gets Migrated

Currently, the tool migrates:
- Boards
- Cards (titles and descriptions)
- Users

Planned migrations:
- Tags to labels
- Checklists
- Attachments
- Comments
- Card positions
- Due dates
- Assignees

## Utility Scripts

- `utils.py`: Connection testing and utility functions
- `test_imports.py`: Module import verification
- `run_tests.py`: Test runner for all tests

## Customization

You can modify the migration process by editing:
- `migrator.py`: Main migration logic
- `kaiten_client/client.py`: Kaiten API interactions (uses official kaiten package)
- `planka_client/client.py`: Planka API interactions

## Troubleshooting

If you encounter issues:
1. Check that your API keys are correct
2. Verify that the API URLs in `config.yaml` are correct
3. Check the logs for error messages
4. Ensure you have the necessary permissions in both systems
5. Test connections using `python utils.py test-both`

## Contributing

Feel free to submit issues or pull requests to improve this tool.