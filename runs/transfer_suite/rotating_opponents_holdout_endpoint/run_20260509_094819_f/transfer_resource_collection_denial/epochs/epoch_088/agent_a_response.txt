def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for tx, ty in res:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer resources where we are closer than opponent; then faster self, then lexicographic
        key = (sd - od, sd, tx, ty)
        if best is None or key < best[0]:
            best = (key, tx, ty)
    _, tx, ty = best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_step = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(nx, ny, ox, oy)
        step_key = (nsd, nod, dx, dy)  # primary: approach target; secondary: keep spacing from opponent
        if best_step is None or step_key < best_step[0]:
            best_step = (step_key, dx, dy)
    return [int(best_step[1]), int(best_step[2])]