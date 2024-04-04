# Connect4 AI Player with Minimax Algorithm

This project implements an artificial intelligence player for the classic game Connect4 using the minimax algorithm with alpha-beta pruning and a transposition table. The AI player is designed to play against a human opponent in a web-based Connect4 game interface.

It is implemented in Python and uses the Selenium WebDriver to interact with the web-based game interface. The AI player dynamically adjusts the search depth based on the number of moves played and uses a transposition table to store previously computed positions. It also includes a timeout mechanism to prevent long computation times for moves.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Features

- Implementation of the minimax algorithm with alpha-beta pruning for Connect4.
- Transposition table for storing previously computed positions.
- Integration with Selenium WebDriver for automating web-based game interaction.
- Dynamic depth adjustment based on the number of moves played.
- Timeout handling for moves to prevent long computation times.

## Installation

1. Clone the repository:
    
    ```bash
    git clone
    ```

2. Install the required Python packages:
    
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Create an account at [Connect4](https://papergames.io/en/connect4).
2. Edit the credentials.json file with the username and password for the web-based game interface.
3. Run the AI player script:
    
    ```bash
    python main.py
    ```
