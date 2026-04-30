def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    if not resources:
        dx, dy = 0, 0
        return [dx, dy]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    tx, ty = resources[0]
    best = md(sx, sy, tx, ty)
    for rx, ry in resources[1:]:
        d = md(sx, sy, rx, ry)
        if d < best:
            best = d
            tx, ty = rx, ry

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d_to_target = md(nx, ny, tx, ty)
            d_to_opp = md(nx, ny, ox, oy)
            on_resource = 1 if (nx, ny) in set(resources) else 0
            candidates.append((d_to_target, -d_to_opp, -on_resource, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [candidates[0][3], candidates[0][4]]