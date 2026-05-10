def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for x, y in unclaimed:
        if inb(x, y):
            adj = abs(x - ox) + abs(y - oy) == 1
            front = 1 if adj else 0
            dist_opp = abs(x - ox) + abs(y - oy)
            # Prefer front (adjacent to opponent), then slightly farther from opponent for safety
            targets.append((front * 100000 + dist_opp * 1000 - (x + y), x, y))
    if targets:
        targets.sort()
        _, tx, ty = targets[0]
    else:
        tx, ty = ox, oy

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist_new = abs(nx - tx) + abs(ny - ty)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        adj_opp = 1 if dist_new <= 1 and abs(nx - ox) + abs(ny - oy) == 1 else 0
        score = adj_opp * 1000000 + dist_opp * 10 - dist_new
        cand = (score, nx, ny, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[3], best[4]]