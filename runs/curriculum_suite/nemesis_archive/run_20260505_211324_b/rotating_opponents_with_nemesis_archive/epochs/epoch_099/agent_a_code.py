def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if inside(nx, ny) else [0, 0]

    # Choose a target where we are likely to arrive first (relative advantage).
    best = None
    best_val = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer winning the race; slight preference for closer targets.
        val = (ds - 0.95 * do) + 0.05 * ds
        key = (val, ds, rx, ry)
        if best_val is None or key < best_val:
            best_val = key
            best = (rx, ry)
    tx, ty = best

    # One-step lookahead on candidate moves.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_self = dist(nx, ny, tx, ty)
        d_opp = dist(ox, oy, tx, ty)
        # Higher is better.
        # Encourage decreasing self distance, discouraging states where opponent is closer.
        score = (-d_self) + 0.35 * (d_self - d_opp)  # if opponent is closer, this becomes more negative
        # Small tie-break toward keeping x/y changes modest for determinism and stability.
        score -= 0.01 * (abs(dx) + abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move