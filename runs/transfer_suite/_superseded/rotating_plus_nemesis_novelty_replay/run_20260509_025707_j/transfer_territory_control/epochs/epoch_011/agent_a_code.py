def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)

    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    self_cells = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp_cells = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_in_neigh8(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_cells:
                cnt += 1
        return cnt

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in self_cells:
            val += 50
        if (nx, ny) in opp_cells:
            val += 80 - 2 * (abs(nx - ox) + abs(ny - oy))
        if (nx, ny) in unclaimed:
            val += 20 + 5 * best_in_neigh8(nx, ny) - 1.5 * (abs(nx - ox) + abs(ny - oy))
        if (nx, ny) not in self_cells and (nx, ny) not in opp_cells and (nx, ny) not in unclaimed:
            val += 8 * (best_in_neigh8(nx, ny) - 0.2 * (abs(nx - ox) + abs(ny - oy)))
        if best is None or val > best_val or (val == best_val and (dx, dy) < tuple(best)):
            best_val = val
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best