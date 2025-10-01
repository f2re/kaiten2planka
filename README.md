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

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your API URLs and keys:
   - `KAITEN_API_URL`: Your Kaiten API URL
   - `KAITEN_API_KEY`: Your Kaiten API key
   - `PLANKA_API_URL`: Your Planka API URL
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
- Checklists (with items)

Planned migrations:
- Tags to labels
- Attachments
- Comments
- Card positions
- Due dates
- Assignees

## Utility Scripts

- `utils.py`: Connection testing and utility functions
- `test_imports.py`: Module import verification
- `run_tests.py`: Test runner for all tests
- `example_checklist_migration.py`: Example script demonstrating checklist migration
- `manage_projects.py`: Project management utilities for Planka (add managers, list projects/users)

## Managing Projects with manage_projects.py

The `manage_projects.py` script provides utilities for managing project managers in Planka. It allows you to add managers to all projects, list projects and users, and other project management functions.

### Setup and Configuration

Before using `manage_projects.py`, ensure your `.env` file has the correct `PLANKA_URL`:

```
PLANKA_URL=https://your-planka-instance.com
```

The script will prompt for your Planka username and password to generate an API token when run.

### Available Operations

The script provides an interactive menu with the following operations:

1. **Add manager to all projects**: Prompts you to select a user and adds them as a manager to all existing projects
2. **Show list of projects**: Displays all projects with their current managers
3. **Show list of users**: Displays all users in the Planka instance
4. **Exit**: Exits the application

### Running the Script

To use the script:

```bash
source venv/bin/activate
python manage_projects.py
```

### Operation Details

#### 1. Adding a Manager to All Projects

This operation allows you to select a user and add them as a manager to all projects in your Planka instance. The script will:

- Identify all projects in the system
- Check if the selected user is already a manager of each project
- Skip projects where the user is already a manager
- Add the user as a manager to projects where they are not yet a manager
- Provide a summary of the operation including:
  - Number of projects where the manager was successfully added
  - Number of projects where the user was already a manager
  - Number of projects where there was an error during the operation

#### 2. Showing List of Projects

This operation displays all projects in the Planka instance with the following information:

- Project name and ID
- List of current managers with their names/username
- Total count of projects

#### 3. Showing List of Users

This operation displays all users in the Planka instance with the following information:

- User name and username
- User email
- User ID
- Total count of users

### Use Cases

#### Case 1: Adding a New Administrator to All Projects
When a new administrator joins your organization, you can quickly add them as a manager to all projects without having to navigate to each project individually.

#### Case 2: Verifying Project Ownership
Use the "Show list of projects" feature to audit which projects have managers assigned and identify projects that might need additional management.

#### Case 3: User Management Overview
Use the "Show list of users" feature to get an overview of all users in your Planka instance, which can be helpful when deciding which user to add as a manager.

### Security Notes

- The script will generate an API token based on your credentials and store it in the .env file for future use
- Ensure that your .env file is properly secured and not committed to version control
- The script only adds users as managers and does not modify other user permissions

## Checklist Migration

The tool now supports migrating checklists from Kaiten to Planka. Checklists are migrated as TaskLists in Planka, with individual checklist items becoming TaskItems.

To migrate checklists for a specific card, you can use the example script:
```bash
source venv/bin/activate
python example_checklist_migration.py
```

Or integrate the checklist migration into your existing migration process using the `migrate_checklists` method in the `KaitenToPlankaMigrator` class.

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