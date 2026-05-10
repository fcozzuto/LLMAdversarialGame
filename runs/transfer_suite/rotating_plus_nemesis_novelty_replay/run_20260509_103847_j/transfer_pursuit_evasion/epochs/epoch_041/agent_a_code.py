def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    res_pos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res_pos.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    if res_pos:
        best = None
        for dx, dy, nx, ny in candidates:
            d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res_pos)
            score = (-d, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    best = None
    for dx, dy, nx, ny in candidates:
        d = abs(nx - ox) + abs(ny - oy)
        score = (-d, dx, dy)
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]