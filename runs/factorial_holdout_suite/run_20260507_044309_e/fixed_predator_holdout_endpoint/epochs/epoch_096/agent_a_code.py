def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (0 if sd <= od else 1, sd, od, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try diagonal, then cardinal, then stay; avoid obstacles deterministically.
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (-dx, -dy)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(cdx), int(cdy)]
    return [0, 0]