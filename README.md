# Game Server README

## How to Run the Server
1. Ensure you have Python installed on your machine.
2. Prepare a `UserInfo.txt` file with usernames and passwords in the format: username:password
3. Run the server using the command:
    `python3 GameServer.py <Server_port> <path_to_UserInfo.txt>`
Replace `<Server_port>` with the desired port number and `<path_to_UserInfo.txt>` with the path to your user information file.

## Authentication State
- When you enter the wrong username or password, you will be repeatedly prompted to input the username and password until you provide the correct one.

## In Hall State
- Users should strictly enter the correct command format:
- `/list`
- `/enter <Room number of not full rooms>`
- Other messages will be regarded as unrecognized.
- If a player does not enter any input after 30 seconds, the server will close the thread and socket, treating it as a disconnection. If the player responds after 30 seconds, they will receive an error message: `An error occurred: [WinError 10053]`, notifying them that the server has already closed the connection due to inactivity.

### Exception Handling
- If a player disconnects while in a room, the server will detect this thread ID and report `user: {thread id} is disconnected`. The player will be removed from the room, and the number of players in the room will be updated accordingly.

## In Game State

### Game Start
- The game state can only be accessed when there are 2 players in the room.

### Game End
- When the game ends, the room will be cleared, the number of players in the room will be set to zero, and the guesses of players for this room will be initialized to `None`.

## Input Format
- The expected input format for guesses is: `/guess false /guess true`
- Capitalized `False` and `True` will also be treated as unrecognized messages.
- If the input format is incorrect, the player will be repeatedly asked to provide a valid guess until successful.

## Disconnection Check
1. Disconnection occurs when one player in the room disconnects.
 - If a player leaves before or after the other player's guess, the remaining player must guess first and will receive the message: `You are the winner` since the other player has quit.
 - If a player made a guess, the guess will be uploaded to the server and remains in the server storage utill the game ends. Even though the player leaves before the other player's guess, the remaining player will receive message as normal.

2. Disconnection occurs when one player is waiting for rooms.
- If a player is in the waiting room and its connection to the server ends suddenly, the server will acknowledge this disconnection and update the room status accordingly. 



