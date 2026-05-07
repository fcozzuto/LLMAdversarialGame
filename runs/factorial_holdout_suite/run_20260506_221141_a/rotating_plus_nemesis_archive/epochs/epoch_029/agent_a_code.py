def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources_raw = observation.get("resources", []) or []
    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not (isinstance(sx, int) and isinstance(sy, int) and 0 <= sx < w and 0 <= sy < h and resources):
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose target resource we can reach sooner (tie-break by being closer).
    best = None
    for tx, ty in resources:
        my_d = man(sx, sy, tx, ty)
        op_d = man(ox, oy, tx, ty)
        # Prefer positive advantage (op_d - my_d), then smaller my_d, then stable position tie-break.
        key = (op_d - my_d, -my_d, -(tx * 10007 + ty * 9176))
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (isinstance(nx, int) and isinstance(ny, int) and 0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        my2 = man(nx, ny, tx, ty)
        op2 = man(ox, oy, tx, ty)
        # Strongly avoid moving into states where opponent would beat us (if we tie/lose, still consider).
        adv_after = op2 - my2
        val = (adv_after, -my2, -(nx * 10007 + ny * 9176))
        candidates.append((val, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: z[0], reverse=True)
    return candidates[0][1]