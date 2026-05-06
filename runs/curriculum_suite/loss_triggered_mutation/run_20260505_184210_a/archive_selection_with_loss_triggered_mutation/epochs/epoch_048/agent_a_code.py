def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources or (sx, sy) in obstacles:
        return [0, 0]

    best = None
    for x, y in resources:
        d = abs(x - sx) + abs(y - sy)
        if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
            best = (d, (x, y))
    tx, ty = best[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dist = abs(tx - nx) + abs(ty - ny)
            candidates.append((dist, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[3], t[4], t[1], t[2]))
    _, dx, dy, _, _ = candidates[0]
    return [dx, dy]