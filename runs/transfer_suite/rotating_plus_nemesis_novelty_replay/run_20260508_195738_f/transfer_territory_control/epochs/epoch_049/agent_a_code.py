def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp_terr = observation.get("opponent_territory", []) or []
    opp_pos = observation.get("opponent_position", None)
    opp = set((p[0], p[1]) for p in opp_terr)
    if opp_pos is not None:
        opp.add((opp_pos[0], opp_pos[1]))
    unclaimed = observation.get("unclaimed_cells", []) or []
    if not unclaimed:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    # Pick best target: unclaimed cell adjacent to opponent territory; otherwise nearest unclaimed.
    best = None
    best_score = None
    for ux, uy in unclaimed:
        if (ux, uy) in obs:
            continue
        adj_opp = 1 if any((nx, ny) in opp for nx, ny in neighbors8(ux, uy)) else 0
        dist = abs(ux - sx) + abs(uy - sy)
        # Prefer edge claiming: high adj_opp, then close, then tie-break deterministically.
        score = (-adj_opp, dist, uy, ux)
        if best_score is None or score < best_score:
            best_score = score
            best = (ux, uy)

    tx, ty = best if best is not None else (sx, sy)

    # Choose move among legal deltas that minimizes distance to target, with a bias toward making progress to the frontier.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        # If step lands adjacent to opponent territory, slightly better (deterministic bias).
        adj = 1 if any((px, py) in opp for px, py in neighbors8(nx, ny)) else 0
        val = (dist, -adj, dy, dx)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]