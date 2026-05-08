def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    neigh8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    dirs9 = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(1,-1),(-1,1),(1,1),(0,0)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def is_adj_to_self(cell):
        x, y = cell
        for dx, dy in neigh8:
            if (x+dx, y+dy) in self_terr:
                return True
        return False

    def is_adj_to_opp(cell):
        x, y = cell
        for dx, dy in neigh8:
            if (x+dx, y+dy) in opp_terr:
                return True
        return False

    best = (0, (0, 0))
    # Base bias: keep expanding from nearest edge, but periodically probe enemy.
    probe_enemy = (observation.get("turn_index", 0) % 10) >= 5

    for dx, dy in dirs9:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        target = (nx, ny)
        val = 0
        if target in self_terr:
            val += 1
            val -= 0.01 * manh((nx, ny), (sx, sy))
        elif target in unclaimed:
            val += 2
            if is_adj_to_self(target):
                val += 2
            if probe_enemy and is_adj_to_opp(target):
                val += 0.5
            val -= 0.02 * manh(target, (sx, sy))
        elif target in opp_terr:
            val += 5
            if probe_enemy:
                val += 2
            val -= 0.01 * manh(target, (sx, sy))
        else:
            # moving into empty non-territory is still possible; slight preference for staying mobile
            if is_adj_to_self(target):
                val += 1
            val -= 0.05 * manh(target, (ox, oy))

        # Secondary tie-breakers to be deterministic
        val -= 0.001 * abs(dx) - 0.0005 * abs(dy)

        if val > best[0] or (val == best[0] and (dx, dy) < best[1]):
            best = (val, (dx, dy))

    return [best[1][0], best[1][1]]