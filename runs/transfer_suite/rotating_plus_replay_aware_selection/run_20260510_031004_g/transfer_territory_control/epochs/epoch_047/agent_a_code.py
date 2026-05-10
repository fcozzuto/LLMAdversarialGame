def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    px, py = observation["opponent_position"]

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def d(a, b, c, e): return abs(a - c) + abs(b - e)

    # Choose a deterministic target: prefer unclaimed adjacent to our territory; else nearest unclaimed.
    frontier = []
    if unclaimed and self_terr:
        for x, y in self_terr:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: 
                        continue
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in unclaimed:
                        frontier.append((nx, ny))
        if frontier:
            target = min(frontier, key=lambda t: (d(sx, sy, t[0], t[1]), t[0], t[1]))
        else:
            target = min(unclaimed, key=lambda t: (d(sx, sy, t[0], t[1]), t[0], t[1]))
    elif unclaimed:
        target = min(unclaimed, key=lambda t: (d(sx, sy, t[0], t[1]), t[0], t[1]))
    else:
        target = None

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0

        if (nx, ny) in unclaimed:
            val += 80
        if (nx, ny) in self_terr:
            val += 15
        if (nx, ny) in opp_terr:
            val += 120  # flipping on entry is strong

        if target is not None:
            val += 30 - d(nx, ny, target[0], target[1])  # closer is better

        # Risk: avoid stepping into contested squares where opponent is at least as close.
        opp_dist = d(px, py, nx, ny)
        my_dist = d(sx, sy, nx, ny)
        if opp_dist <= my_dist:
            val -= 25

        # Micro-preference to keep moving (reduce stagnation) unless clearly best.
        if dx == 0 and dy == 0:
            val -= 3

        if val > bestv or (val == bestv and (dx, dy) < best):
            bestv = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]