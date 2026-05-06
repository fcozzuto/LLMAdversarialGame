def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target that we can reach first, and that is less immediately "sweepable" on opponent's row.
    best_t = None
    best_v = None
    for t in resources:
        ds = dist((sx, sy), t)
        do = dist((ox, oy), t)
        row_pen = 2.0 if abs(t[1] - oy) <= 1 else 0.0
        val = (do - ds) - 0.35 * ds - row_pen
        if best_v is None or val > best_v:
            best_v, best_t = val, t

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate one-step safety + commitment to target.
    best_m = (0, 0)
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = dist((nx, ny), (tx, ty))
        d_from_opp = dist((nx, ny), (ox, oy))
        # If opponent is sweeping near our target row, prefer breaking line.
        line_break = 1.5 if abs(ny - oy) > abs(sy - oy) else 0.0
        # Prefer reducing distance to target without drifting too close to opponent.
        s = (-d_to_t) + 0.18 * d_from_opp + line_break + (0.08 if (nx, ny) == (tx, ty) else 0.0)
        if best_s is None or s > best_s:
            best_s, best_m = s, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]