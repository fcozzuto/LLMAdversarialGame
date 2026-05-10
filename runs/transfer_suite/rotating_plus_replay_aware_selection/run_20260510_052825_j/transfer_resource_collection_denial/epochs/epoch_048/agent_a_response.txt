def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    valid = [(p[0], p[1]) for p in resources if inb(p[0], p[1]) and (p[0], p[1]) not in obstacles]
    if not valid:
        return [0, 0]

    best_target = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (0 if sd < od else 1, sd - od, sd, od, rx, ry)
        if best_target is None or key < best_target[0]:
            best_target = (key, (rx, ry))
    tx, ty = best_target[1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my = cheb(nx, ny, tx, ty)
        op = cheb(ox, oy, tx, ty)
        # Prefer faster capture; if equal, force opponent worse (denier behavior).
        # Small tie-breaker to keep movement stable (prefer fewer changes).
        val = (my - op, my, op, abs(dx) + abs(dy))
        if best is None or val < best[0]:
            best = (val, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]