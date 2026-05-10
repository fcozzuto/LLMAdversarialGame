def choose_move(observation):
    w = int(observation.get("grid_width") or 0) or 8
    h = int(observation.get("grid_height") or 0) or 8
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    candidates = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    dx_best = 0
    dy_best = 0
    best = -10**18

    def score(nx, ny):
        d = abs(nx - ox) + abs(ny - oy)
        return -d * 10 - (1 if (nx, ny) in obs else 0)

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            sc = score(nx, ny)
            if sc > best:
                best = sc
                dx_best, dy_best = dx, dy

    if best == -10**18:
        return [0, 0]
    return [int(dx_best), int(dy_best)]