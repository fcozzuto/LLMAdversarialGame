def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if res:
        best_t = None
        best_val = 10**18
        for rx, ry in res:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; slightly penalize being closer to opponent targets
            val = ds - 0.85 * do
            if val < best_val:
                best_val = val
                best_t = (rx, ry)

        tx, ty = best_t
        # Evaluate candidate next moves by how much they improve "being before opponent" for target
        best_m = (0, 0)
        best_s = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # Primary: maximize advantage; Secondary: reduce own distance; Tertiary: move toward target deterministically
            s = (0.85 * do - ds) * 1000 - ds
            if (dx, dy) == best_m:
                continue
            if s > best_s:
                best_s = s
                best_m = (dx, dy)
        return [int(best_m[0]), int(best_m[1])]

    # No visible resources: move to increase distance from opponent (deterministic, safe)
    best_m = (0, 0)
    best_d = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        if d > best_d:
            best_d = d
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]