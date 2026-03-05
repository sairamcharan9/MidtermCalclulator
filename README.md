<div align="center">
  <h1>🧮 Advanced Calculator Application</h1>
  <p><i>A beautifully styled, fully-featured command-line calculator built with Python.</i></p>

  ![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
  ![Coverage](https://img.shields.io/badge/Coverage-97%25-brightgreen.svg)
  ![Design Patterns](https://img.shields.io/badge/Design_Patterns-Facade_|_Observer_|_Strategy-purple.svg)
</div>

<br />

## 📸 Showcase & REPL Demo

Experience our intuitive, color-coded REPL interface in action. The application features robust syntax highlighting for commands, success messages, operational status, and errors natively leveraging `colorama` for a seamless user experience!

<div align="center">
  <img src="screenshots/image%20copy.png" width="48%" />
  <img src="screenshots/image%20copy%203.png" width="48%" />
</div>

<div align="center" style="margin-top: 10px;">
  <img src="screenshots/image%20copy%202.png" width="98%" />
</div>

<div align="center" style="margin-top: 10px;">
  <img src="screenshots/image%20copy%204.png" width="98%" />
</div>

---

## 📖 Project Description

This project is a sophisticated command-line calculator application built with Python, showcasing the integration of advanced software design patterns (Facade, Observer, Strategy, and Memento) to create a modular, extensible, and maintainable system. It moves beyond basic arithmetic to offer a rich feature set including persistent history, undo/redo functionality, and comprehensive logging, all configurable via environment variables.

The core of the application is an interactive Read-Eval-Print Loop (REPL), providing a seamless user experience for performing calculations with full color-coded feedback!

### 🌟 Key Features

- **🎨 Color-Coded Interface**: Intuitive feedback with Green results, Red errors, Blue history, and Magenta branding.
- **⚡ Advanced Arithmetic**: Supports `add`, `subtract`, `multiply`, `divide`, `power`, `root`, `modulus`, `int_divide`, `percent`, `abs_diff`, and `factorial`.
- **🔄 Undo/Redo System**: Full state management allowing you to revert or repeat any calculation actions.
- **💾 Persistent History**: Seamlessly manages calculation history using `pandas`, with CSV save/load support.
- **🛠️ Design Patterns Focused**: Implements clean architecture using Facade, Strategy, Observer, and Memento patterns.
- **🛡️ Robust Validation**: Comprehensive input validation and custom exception handling for all operations.
- **📊 Detailed Logging**: Centralized logging system capturing all events and errors for auditability.

## 🚀 Installation & Setup

### 1. Clone & Environment
```bash
git clone https://github.com/your-username/calculator-app.git
cd calculator-app
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Usage
```bash
python main.py
```

---

## 📚 All Available Commands

The application supports a rich set of arithmetic and special commands.

### Arithmetic Commands

These commands perform standard calculations. All except `factorial` require two numbers.

| Command      | Description                                                    | Usage Example         |
| :----------- | :------------------------------------------------------------- | :-------------------- |
| `add`        | Returns the sum of two Decimal numbers.                        | `add 10 5`            |
| `subtract`   | Returns the difference between two Decimal numbers.            | `subtract 10 5`       |
| `multiply`   | Returns the product of two Decimal numbers.                    | `multiply 10 5`       |
| `divide`     | Returns the quotient of two Decimal numbers.                   | `divide 10 5`         |
| `power`      | Returns the base `a` raised to the power of `b`.               | `power 2 3`           |
| `root`       | Calculates the `b`-th root of `a`.                             | `root 27 3`           |
| `modulus`    | Returns the remainder of the division of `a` by `b`.           | `modulus 10 3`        |
| `int_divide` | Returns the integer part of the quotient of `a` divided by `b`. | `int_divide 10 3`     |
| `percent`    | Calculates what percentage `a` is of `b`.                      | `percent 50 200`      |
| `abs_diff`   | Returns the absolute difference between `a` and `b`.           | `abs_diff 5 10`       |
| `factorial`  | Calculates the factorial of a non-negative integer.            | `factorial 5`         |

### Special Commands

These commands handle application-level actions like history management, help, and state manipulation.

| Command        | Description                                  | Usage Example   |
| :------------- | :------------------------------------------- | :-------------- |
| `greet`        | Displays a welcome message.                  | `greet`         |
| `help` or `?`  | Shows a detailed list of all commands.       | `help`          |
| `history`      | Displays the calculation history.            | `history`       |
| `clear`        | Clears the entire calculation history.       | `clear`         |
| `undo`         | Reverts the last calculation or action.      | `undo`          |
| `redo`         | Re-applies the last undone action.           | `redo`          |
| `save`         | Manually saves the history to a CSV file.    | `save`          |
| `load`         | Manually loads the history from a CSV file.  | `load`          |
| `exit` or `quit` | Exits the calculator application.          | `exit`          |

---

## 🖥️ REPL Usage Examples

Here is a sample session demonstrating common interactions:

```
> greet
Hello! Welcome to the calculator.
> add 25 17
Result: 42.00
> power 2 8
Result: 256.00
> history
=== Calculation History ===
  1. 25 add 17 = 42.00
  2. 2 power 8 = 256.00

Total: 2 calculation(s)
> undo
Undo successful. History now contains 1 calculation(s).
> history
=== Calculation History ===
  1. 25 add 17 = 42.00

Total: 1 calculation(s)
> exit
Exiting the calculator. Goodbye!
```

## ⚙️ Configuration

Customize the application via the `.env` file:

```env
CALCULATOR_HISTORY_DIR=data
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=2
CALCULATOR_MAX_INPUT_VALUE=1e12
```

---

## 🧪 Testing and Quality

We maintain high code quality standards through comprehensive testing and CI/CD integration.

### Running Tests
To execute the test suite and check coverage:
```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

### GitHub Actions (CI)
Our automated workflow handles:
- ✅ Dependency installation
- ✅ Code linting and standards
- ✅ Cross-platform test execution
- ✅ Coverage threshold enforcement

---

---

<div align="center">
  <p>Developed with ❤️ for Advanced Software Development</p>
</div>
