def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter_list = observation.get("self_territory") or []
    opp_ter_list = observation.get("opponent_territory") or []
    unclaimed_list = observation.get("unclaimed_cells") or []
    obstacles_list = observation.get("obstacles") or []

    self_ter = set((int(p[0]), int(p[1])) for p in self_ter_list if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set((int(p[0]), int(p[1])) for p in opp_ter_list if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in unclaimed_list if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x, y, a, b): return abs(x - a) + abs(y - b)
    def neighbors8(x, y):
        return ((x+1,y),(x-1,y),(x,y+1),(x,y-1),(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1))

    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in self_ter:
            val += 2
        elif (nx, ny) in unclaimed:
            val += 10
        elif (nx, ny) in opp_ter:
            val += 8
        else:
            val += 1

        # Progress toward opponent
        val += (30 - md(nx, ny, ox, oy)) * 0.5

        # Frontier extension: prefer moves adjacent to our territory
        adj_self = any(p in self_ter for p in neighbors8(nx, ny))
        if adj_self:
            val += 4

        # Avoid stepping into our own territory edge too early by slight penalty for staying still
        if dx == 0 and dy == 0:
            val -= 3

        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]