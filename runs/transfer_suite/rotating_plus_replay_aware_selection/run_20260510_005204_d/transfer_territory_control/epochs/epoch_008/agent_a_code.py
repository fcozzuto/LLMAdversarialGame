def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    self_terr = observation.get("self_territory", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []
    obstacles = observation.get("obstacles", []) or []

    self_set = set((p[0], p[1]) for p in self_terr)
    opp_set = set((p[0], p[1]) for p in opp_terr)
    uncla_set = set((p[0], p[1]) for p in unclaimed)
    obs_set = set((p[0], p[1]) for p in obstacles)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**18

    cur_dop = md(sx, sy, ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
            dx, dy = 0, 0
        dop = md(nx, ny, ox, oy)
        dc = -md(nx, ny, cx, cy)  # closer to center is better
        cell_score = 0
        if (nx, ny) in uncla_set:
            cell_score += 6
        if (nx, ny) in opp_set:
            cell_score += 3  # flipping on entry is possible, but don't overcommit
        if (nx, ny) in self_set:
            cell_score += 2

        # Core preference: gain safety (stay away from opponent), expand to unclaimed, only lightly consider invasions.
        score = 3 * (dop - cur_dop) + 0.9 * dc + cell_score
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]