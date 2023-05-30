from pwn import *
from ctypes import *
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
sh = remote(HOST, int(PORT))




libc_native = CDLL("libc.so.6")
seed = libc_native.time(0)

def get_rand(t):
  v2 = ['']*4
  v3 = ['']*16
  v4 = ['']*16
  v2[0] = "cozy"
  v2[1] = "medium-sized"
  v2[2] = "spacious"
  v2[3] = "massive"
  v3[0] = "bookshelves"
  v3[1] = "fireplaces"
  v3[2] = "suits of armor"
  v3[3] = "tables"
  v3[4] = "chests"
  v3[5] = "beds"
  v3[6] = "paintings"
  v3[7] = "statues"
  v3[8] = "tapestries"
  v3[9] = "candelabras"
  v3[10] = "chairs"
  v3[11] = "fountains"
  v3[12] = "mirrors"
  v3[13] = "rugs"
  v3[14] = "curtains"
  v3[15] = "chess sets"
  v4[0] = "Art Deco"
  v4[1] = "Baroque"
  v4[2] = "Classical"
  v4[3] = "Colonial"
  v4[4] = "Contemporary"
  v4[5] = "Country"
  v4[6] = "Gothic"
  v4[7] = "Industrial"
  v4[8] = "Mediterranean"
  v4[9] = "Minimalist"
  v4[10] = "Neoclassical"
  v4[11] = "Renaissance"
  v4[12] = "Rococo"
  v4[13] = "Romantic"
  v4[14] = "Rustic"
  v4[15] = "Victorian"

  v = t.split('you find yourself standing in a ')[-1].split(' space.')[0]
  a = (v2.index(v))
  v = t.split('The walls are adorned with ')[-1].split(' and ')[0]
  b = (v3.index(v))

  v = t.split('and a two large ')[-1].split(' dominate')[0]
  c = (v3.index(v))

  v = t.split('designed in the ')[-1].split(' style')[0]
  d = (v4.index(v))

  v = t.split('You see ')[-1].split(' flowers in a')[0]
  e = int(v)
  # print(e)

  v = t.split('a window you stop to count ')[-1].split(' stars.')[0]
  f = int(v)
  # print(f)
  v = a + (b<<2) + (c<<6) + (d<<10) + (f<<14)
  # print(v)
  return v

t = 'As you step into the room, you find yourself standing in a massive space. The walls are adorned with paintings and a two large fountains dominate the center of the room. You see 20 flowers in a vase, and through a window you stop to count 118612 stars. The room appears well designed in the Industrial style.'
print(get_rand(t))
t = 'As you step into the room, you find yourself standing in a spacious space. The walls are adorned with chess sets and a two large candelabras dominate the center of the room. You see 0 flowers in a vase, and through a window you stop to count 111136 stars. The room appears well designed in the Contemporary style.'
print(get_rand(t))


# stdout = process.PTY
# stdin = process.PTY
# sh = process(['./ld-linux-x86-64.so.2', './challenge'], env={
#   'LD_PRELOAD':'./libc.so.6'
# }, stdout=stdout, stdin=stdin)
sh.recvuntil('You are in room (1, 1)\n')

v = get_rand(sh.recvline().strip().decode())
print(v)

found = False
found_seed = 0
found_cnt = 0
for i in range(-60,60):
  cand_seed = seed + i
  # print(cand_seed)
  libc_native.srand(cand_seed)
  cnt = 0
  for j in range(1000):
    g = libc_native.rand()
    cnt += 1
    # print(g)
    if g == v:
      print('seed: ', cand_seed)
      print('cnt: ', cnt)
      found_cnt = cnt
      found_seed = cand_seed
      # print()
      found = True
assert found
libc_native.srand(found_seed)
for i in range(found_cnt):
  g = libc_native.rand()
# while True:
#   next = libc_native.rand()
#   if next % 1213 == 1212:
#     break
#   sh.sendlineafter(b'torment: ', b'n')



sh.sendlineafter(b'torment: ', b'a')
sh.recvuntil(b'maze.\n')

maze = ""

for i in range(29):
  maze += sh.recvline().decode() # .strip().decode()

print('>>',maze,'<<')

steps = []

def solve_maze(maze):
  # Splitting the maze into rows
  maze = maze.strip().split('\n')

  # Function to find the character position in the maze
  def find_char(maze, char):
    for i, row in enumerate(maze):
      for j, cell in enumerate(row):
        if cell == char:
          return i, j
    return None

  # Finding the starting position and target position
  start_pos = find_char(maze, '@')
  target_pos = find_char(maze, '*')

  # Defining the movements
  movements = {'n': (-1, 0), 'e': (0, 1), 's': (1, 0), 'w': (0, -1)}

  # Function to find the next valid moves from a given position
  def find_valid_moves(position):
    valid_moves = []
    for move, (dx, dy) in movements.items():
      next_x, next_y = position[0] + dx, position[1] + dy
      if (
        0 <= next_x < len(maze) and
        0 <= next_y < len(maze[next_x]) and
        maze[next_x][next_y] != '#'
      ):
        valid_moves.append((move, (next_x, next_y)))
    return valid_moves

  # Function to backtrack and print the steps
  def print_steps(path):
    for move, _ in path[1:]:
      print(move, end='')
      steps.append(move)
    print()

  # Function to recursively search for the target
  def search(position, path):
    if position == target_pos:
      print_steps(path)
      return True

    valid_moves = find_valid_moves(position)
    for move, next_position in valid_moves:
      maze[position[0]] = maze[position[0]][:position[1]] + '#' + maze[position[0]][position[1]+1:]
      if search(next_position, path + [(move, next_position)]):
        return True
      maze[position[0]] = maze[position[0]][:position[1]] + '.' + maze[position[0]][position[1]+1:]

    return False

  # Starting the recursive search
  return search(start_pos, [('', start_pos)])

print ('!!',solve_maze(maze))
print(steps)
blob = ''
sh.recvuntil('torment: ')
for each in steps[:-1]:
  sh.sendline(each)
  next = libc_native.rand()

  blob = sh.recvuntil('torment: ')

poss = blob.split(b'do?\ngo ')[-1]
if b'(n)' not in poss:
  op = 'n'
elif b'(e)' not in poss:
  op = 'e'
elif b'(s)' not in poss:
  op = 's'
elif b'(w)' not in poss:
  op = 'w'




last_step = steps[-1]
while True:
  next = libc_native.rand()
  if next % 1213 == 1212:
    break
  sh.sendline(op)
  sh.recvuntil('torment: ')
sh.sendline(last_step)


sh.sendline(b'./submitter')
flag = sh.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)