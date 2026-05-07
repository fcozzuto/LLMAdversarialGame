def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    options = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            options.append((dx, dy, nx, ny))

    def manhattan(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no resources, move to safer corner (avoid opponent if possible)
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            sc = (abs(cx - sx) + abs(cy - sy)) + 0.01 * (abs(cx - ox) + abs(cy - oy))
            if best is None or sc < best[0]:
                best = (sc, cx, cy)
        if best is None:
            return [0, 0]
        cx, cy = best[1], best[2]
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        if (sx + dx, sy + dy) in obstacles or not (0 <= sx + dx < w and 0 <= sy + dy < h):
            # fall back to cardinal that gets closer
            for ddx, ddy in [(dx, 0), (0, dy), (dx, dy), (0, 0)]:
                nx, ny = sx + ddx, sy + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [int(ddx), int(ddy)]
            return [0, 0]
        return [int(dx), int(dy)]

    # Choose move that makes us most likely to reach a "contested" resource first
    best_move = None
    best_score = None
    for dx, dy, nx, ny in options:
        # Evaluate best target from this next position
        best_target_score = None
        for tx, ty in resources:
            myd = manhattan(nx, ny, tx, ty)
            opd = manhattan(ox, oy, tx, ty)
            # Prefer closer resources; if opponent also close, prioritize those where we are already ahead
            score = myd - 0.85 * (opd - myd)  # smaller is better; rewards being earlier than opponent
            # Small tie-break: prefer targets more "central" to reduce path blocking likelihood
            score += 0.01 * (abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2))
            if best_target_score is None or score < best_target_score:
                best_target_score = score
        # Also discourage stepping away from all resources
        overall = best_target_score + 0.02 * (manhattan(nx, ny, sx, sy))
        if best_score is None or overall < best_score:
            best_score = overall
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]