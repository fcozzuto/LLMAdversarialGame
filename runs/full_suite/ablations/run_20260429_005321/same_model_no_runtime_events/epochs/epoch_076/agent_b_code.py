def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        nearest = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
        tx, ty = nearest
    else:
        tx, ty = ox, oy

    def score(nx, ny):
        # Prefer closer to target, avoid letting opponent get closer (roughly).
        d_self = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(ox - tx) + abs(oy - ty)
        d_opp_next = abs(ox - tx) + abs(oy - ty)  # opponent move unknown; keep stable
        return d_self * 10 - (0 if resources else 1) - d_opp

    best = None
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = score(nx, ny)
        if best_s is None or s < best_s:
            best_s = s
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]