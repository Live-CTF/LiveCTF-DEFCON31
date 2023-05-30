#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <stdbool.h>

#define ROWS 30
#define COLS 30

char spinner[4] = "|/-\\";
int spinner_counter = 0;
bool show_maze = 0;
int random_counter = 0;

void winner() {
  printf("Congratulations! You have solved the maze!\n");
  system("/bin/sh");
  exit(0);
}

// Function to generate a random number between min and max (inclusive)
int rand_range(int min, int max) {
  printf("\r%c", spinner[spinner_counter]);
  spinner_counter = (spinner_counter + 1) % strlen(spinner);
  fflush(stdout);
  usleep(5000);
  random_counter+=1;
  return rand() % (max - min + 1) + min;
}

void randomDescription() {
  const char* sizes[] = {"cozy", "medium-sized", "spacious", "massive"};
  const char* objects[] = {"bookshelves", "fireplaces", "suits of armor", "tables", 
    "chests", "beds", "paintings", "statues", 
    "tapestries", "candelabras", "chairs", "fountains", 
    "mirrors", "rugs", "curtains", "chess sets" };
  const char* styles[] = {"Art Deco", "Baroque", "Classical", "Colonial", "Contemporary", 
    "Country", "Gothic", "Industrial", "Mediterranean", "Minimalist", 
    "Neoclassical", "Renaissance", "Rococo", "Romantic", "Rustic", 
    "Victorian"};

  random_counter+=1;
  int64_t room_random = rand();
  int size_index = 0b11 & room_random;
  int object_index_1 = (room_random >> 2) & 0b1111;
  int object_index_2 = (room_random >> 6) & 0b1111;
  int style_index = (room_random >> 10) & 0b1111;
  int flower_count = (room_random >> 14) & 0b11111;
  int star_count = room_random >> 14;

  // printf("Size index: %d\nOb1: %d, Ob2: %d, Style: %d, Stars: %d\n\n", size_index, object_index_1, object_index_2, style_index, star_count);

  printf("As you step into the room, you find yourself standing in a %s space. The walls are adorned with %s and a two large %s dominate the center of the room. You see %d flowers in a vase, and through a window you stop to count %d stars. The room appears well designed in the %s style.\n",
         sizes[size_index], objects[object_index_1], objects[object_index_2], 
         flower_count, star_count, styles[style_index]);
}

void display_maze(char maze[ROWS][COLS], int player_x, int player_y) {
  // Display the maze with the player's current position highlighted
  for (int i = 0; i < ROWS; i++) {
    for (int j = 0; j < COLS; j++) {
      if (i == player_x && j == player_y) {
        printf("@");
      } else {
        printf("%c", maze[i][j]);
      }
    }
    printf("\n");
  }
}

// Recursive function to generate the maze
void generate_maze(char maze[ROWS][COLS], int x, int y, bool lastrun) {
  // Mark the current cell as visited
  maze[x][y] = '.';

  // Create a list of neighbors
  int neighbors[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

  // Randomly shuffle the list of neighbors
  for (int i = 3; i > 0; i--) {
    int j = rand_range(0, i);
    int temp_x = neighbors[i][0];
    int temp_y = neighbors[i][1];
    neighbors[i][0] = neighbors[j][0];
    neighbors[i][1] = neighbors[j][1];
    neighbors[j][0] = temp_x;
    neighbors[j][1] = temp_y;
  }

  // Visit each neighbor in a random order
  for (int i = 0; i < 4; i++) {
    int new_x = x + neighbors[i][0] * 2;
    int new_y = y + neighbors[i][1] * 2;

    if (new_x >= 1 && new_x < ROWS - 1 && new_y >= 1 && new_y < COLS - 1 && maze[new_x][new_y] == '#') {
      // Break the wall between the current cell and the neighbor
      maze[x + neighbors[i][0]][y + neighbors[i][1]] = '.';

      // Recursively visit the neighbor
      generate_maze(maze, new_x, new_y, false);
    }
  }

  // Add an exit point from the right or bottom side of the maze
  if (lastrun)
  {
    int exit_side = rand_range(0, 1); // randomly choose which side the exit will be on

    if (exit_side == 0) { // exit on the right side
      while(true)
      {
        int exit_x = rand_range(1, ROWS - 2);
        // confirm exit is reachable
        if (maze[exit_x][COLS - 3] == '.')
        {
          maze[exit_x][COLS - 2] = '*';
          break;
        }
      }
    } else { // exit on the bottom side
      while(true)
      {
        int exit_y = rand_range(1, COLS - 2);
        // confirm exit is reachable
        if (maze[ROWS - 3][exit_y] == '.')
        {
          maze[ROWS - 2][exit_y] = '*';
          break;
        }
      }
    }
    // Trim extra padding, not sure why it's there lol
    for (int i = 0; i < ROWS; i++)
      maze[ROWS - 1][i] = ' ';
    for (int j = 0; j < COLS; j++)
      maze[j][COLS - 1] = ' ';
  }
}

bool validwalk(char maptile)
{
  return maptile >= '\'' && maptile <= '/';
}

int main() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);
  srand(time(NULL));

  // Create a 2D array to represent the maze
  char maze[ROWS][COLS];

  // Initialize the small maze with walls
  for (int i = 0; i < ROWS; i++) {
    for (int j = 0; j < COLS; j++) {
      maze[i][j] = '#';
    }
  }

  // Generate the maze
  printf("Reticulating splines... \n");
  generate_maze(maze, 1, 1, true);

  // Print the maze
  printf("\n\nWelcome to the maze!\n");
  int x = 1;
  int y = 1;
  int genroom = 1; 

  while (1) {
    if (show_maze)
      display_maze(maze, x, y);
    printf("You are in room (%d, %d)\n", x, y);
    if (genroom)
      randomDescription();
    else
      genroom = 1;

    // Get input from the user to move to a new room
    char input;
    printf("Which would you like to do?\n");
    if (validwalk(maze[x - 1][y]))
      printf("go (n)orth, ");
    if (validwalk(maze[x + 1][y]))
      printf("go (s)outh, ");
    if (validwalk(maze[x][y - 1]))
      printf("go (w)est, ");
    if (validwalk(maze[x][y + 1]))
      printf("go (e)ast, ");
    printf("or (q) end the torment");

    printf(": ");

    scanf(" %c", &input);
    printf("\n");

    // Move the player to the new room
    switch (input) {
      case 'n':
        if (validwalk(maze[x - 1][y])) {
          x--;
        }
        break;
      case 's':
        if (validwalk(maze[x + 1][y])) {
          x++;
        }
        break;
      case 'w':
        if (validwalk(maze[x][y - 1])) {
          y--;
        }
        break;
      case 'e':
        if (validwalk(maze[x][y + 1])) {
          y++;
        }
        break;
      case 'a':
        printf("You cast arcane eye and send your summoned magical eye above the maze.\n");
        show_maze = true;
        genroom = 0;
        break;
      case 'q':
        exit(0);
        break;
    }
    if (maze[x][y] == '*')
    {
      // LOL, EZMODE
      //printf("random counter %d", random_counter);
      if (rand() % 1213 == 1212)
        {
          printf("You successfully exit the maze!\n");
          winner();
          break;
          exit(0);
        }
      else
      {
        printf("Just as you are about to exit, a displacer beast captures you. You die.\n");
        exit(0);
      }
    }
  }


  return -1;
}

