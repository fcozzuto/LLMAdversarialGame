def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # retreat while slightly steering toward center to keep future options
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dist_opp = manh(nx, ny, ox, oy)
            center = abs(nx - cx) + abs(ny - cy)
            v = (dist_opp, -center)
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Heuristic: maximize advantage to capture a resource soonest; penalize giving opponent head start.
    # Also bias toward resources that lie off the direct "row/col sweep" line by a small amount.
    def best_value(nx, ny):
        # Encourage being closer sooner than opponent for the same resource
        bestv = None
        bestcount = 0
        for rx, ry in resources:
            d_self = manh(nx, ny, rx, ry)
            d_opp = manh(ox, oy, rx, ry)
            # If we can arrive no later than opponent, big bonus; if behind, reduced but still consider.
            rel = d_opp - d_self
            # Small sweep-avoid bias: prefer targets not on same row or column if opponent is aligned.
            aligned_pen = 0
            if oy == ry:
                aligned_pen += 0.5
            if ox == rx:
                aligned_pen += 0.5
            # Tie-break: prefer closer resource to reduce time-in-danger.
            v = (rel * 10 - d_self - aligned_pen, -d_self)
            if bestv is None or v > bestv:
                bestv = v
                bestcount += 1
        return bestv

    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = best_value(nx, ny)
        if best_score is None or v > best_score:
            best_score = v
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]