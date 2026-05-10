def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)
    opp_set = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un_set = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    self_set = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_count(x, y, s):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in s:
                    c += 1
        return c

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        val = 0
        if (nx, ny) in opp_set:
            val += 9
        elif (nx, ny) in un_set:
            val += 5
        elif (nx, ny) in self_set:
            val += 2

        val += 3 * neigh_count(nx, ny, self_set)
        val += 2 * neigh_count(nx, ny, opp_set)

        # Prefer steering toward center while expanding
        val += -0.06 * (abs(nx - cx) + abs(ny - cy))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]