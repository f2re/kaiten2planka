# Qwen Code Configuration

This file contains instructions for customizing interactions with Qwen Code.

## Project Overview

This project is called `kaiten2planka`. It is a Python application for migrate data from Kaiten to Planka. To get Kaiten data you must use kaiten package and it functions. To write to Planka you must use planka package and it functions, but to work with users list and accounts in planka tou must implement own function and dont use Planka package. You must migrate cards, text, description of cards, checklists, attachments, users, tags and etc.

## Preferred Tools & Technologies

- **Language:** Python
- **Package Management:** `pip`
- **Linting:** `ruff`
- **Type Checking:** `mypy`
- **Documentation:** Markdown
- **Debugging:** Use `print` statements and the `icecream` (ic) package for debugging. You must import it on each file `from iceream import ic` where you want to print message.
- **Packages:** For Kaiten use kaiten package.

## Code Style & Conventions

- Follow PEP 8 style guide for Python code.
- Use meaningful variable and function names.
- Write clear and concise comments, focusing on *why* rather than *what*.
- Adhere to existing project conventions observed in the codebase.
- Use `icecream` for debugging: `from icecream import ic; ic(variable)`.

## Programming Principles

### KISS (Keep It Simple, Stupid)

- Strive for simplicity in design and implementation.
- Avoid unnecessary complexity.
- Write code that is easy to read and understand.

### SOLID Principles

- **Single Responsibility Principle (SRP):** A class should have only one reason to change.
- **Open/Closed Principle (OCP):** Software entities should be open for extension but closed for modification.
- **Liskov Substitution Principle (LSP):** Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.
- **Interface Segregation Principle (ISP):** Clients should not be forced to depend on interfaces they do not use.
- **Dependency Inversion Principle (DIP):** High-level modules should not depend on low-level modules. Both should depend on abstractions.

## Best Programming Patterns

- **Use descriptive names:** Choose names that clearly express the purpose of variables, functions, and classes.
- **Write small functions:** Functions should be small and focused on a single task.
- **Avoid deep nesting:** Use guard clauses and early returns to reduce nesting levels.
- **Prefer composition over inheritance:** Favor object composition to achieve code reuse and flexibility.
- **Use design patterns appropriately:** Apply well-known design patterns (e.g., Factory, Singleton, Observer) when they solve a specific problem effectively.
- **Write pure functions:** Functions that always return the same output for the same input and have no side effects are easier to test and reason about.

## Workflow Preferences

- Always verify changes with relevant tests.
- Run linters and type checkers before committing.
- Provide clear and concise explanations for significant changes.
- Ask for clarification if requirements are ambiguous.

## Communication Style

- Be concise and direct in responses.
- Use GitHub-flavored Markdown for formatting.
- Focus on providing actionable information.

## Bash commands and script execution

to execute script and pip you must activate venv first:

```bash
source venv/bin/activate
```
