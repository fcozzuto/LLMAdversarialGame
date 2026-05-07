def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

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

    best = None
    for x, y in resources:
        d = abs(sx - x)
        dy = abs(sy - y)
        if dy > d:
            d = dy
        if best is None or d < best[0] or (d == best[0] and (x, y) < best[1]):
            best = (d, (x, y))
    _, (tx, ty) = best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                nx_d = abs(nx - tx)
                ny_d = abs(ny - ty)
                dist = nx_d if nx_d > ny_d else ny_d
                candidates.append((dist, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [candidates[0][1], candidates[0][2]]