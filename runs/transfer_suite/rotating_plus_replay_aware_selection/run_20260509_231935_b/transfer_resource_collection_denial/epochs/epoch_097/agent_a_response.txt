def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or []) if p and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def risk(x, y):
        r = 0
        for kx in (-1, 0, 1):
            for ky in (-1, 0, 1):
                if kx == 0 and ky == 0:
                    continue
                if (x + kx, y + ky) in obstacles:
                    r += 1
        return r

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = (risk(nx, ny), man(nx, ny, w // 2, h // 2), 0, dx, dy)
            if best is None or v < best:
                best = v
        return [best[3], best[4]] if best is not None else [0, 0]

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    best = None
    # Maximize our best "reach advantage" over all visible resources from the next cell.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        r = risk(nx, ny)
        best_adv = -10**9
        best_dist = 10**9
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_dist):
                best_adv = adv
                best_dist = sd
        # Tie-break: prefer larger advantage, then closer to some resource, then safer cell, then deterministic move order.
        v = (-best_adv, best_dist, r, dx, dy)
        if best is None or v < best:
            best = v
    return [best[3], best[4]] if best is not None else [0, 0]