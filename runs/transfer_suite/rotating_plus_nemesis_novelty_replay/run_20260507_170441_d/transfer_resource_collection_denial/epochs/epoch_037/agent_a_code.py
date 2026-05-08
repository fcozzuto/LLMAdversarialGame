def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None:
            obst.add((p[0], p[1]))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        best_r = None
        for rx, ry in resources:
            ds = mdist(nx, ny, rx, ry)
            if best_r is None or ds < best_r[0]:
                best_r = (ds, rx, ry)
        ds, rx, ry = best_r

        do = mdist(ox, oy, rx, ry)

        # Race heuristic: prefer resources we reach sooner than opponent.
        # Tie-break: closer is better; small preference to move (avoid staying).
        score = (do - ds) * 2.0 + (-ds) + (0.15 * do) - (0.08 if dx == 0 and dy == 0 else 0.0)

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]