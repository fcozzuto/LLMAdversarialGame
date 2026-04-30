def choose_move(observation):
    x0, y0 = observation["self_position"]
    xo, yo = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy)

    # Pick a contested target we have advantage on (or least disadvantage if none)
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = dist(x0, y0, rx, ry)
        do = dist(xo, yo, rx, ry)
        adv = do - ds  # positive means we are closer
        key = (-(adv), ds, rx, ry)  # min by this means max adv, then closer
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        # Fallback: move toward center while avoiding obstacles
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best_r = (tx, ty)

    tx, ty = best_r
    # Candidate moves: 8-direction + stay
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Objective: minimize distance to target; if tied, maximize distance from opponent (reduce their ability to contest)
        if isinstance(tx, float):
            d_tar = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            d_opp = dist(nx, ny, xo, yo)
        else:
            d_tar = dist(nx, ny, tx, ty)
            d_opp = dist(nx, ny, xo, yo)
        # Small penalty for moving into opponent vicinity and small preference for staying closer to target
        score = d_tar - 0.05 * d_opp
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_m):
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]