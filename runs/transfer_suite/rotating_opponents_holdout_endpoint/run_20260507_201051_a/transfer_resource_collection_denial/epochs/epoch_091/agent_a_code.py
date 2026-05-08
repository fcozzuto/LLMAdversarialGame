def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
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
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # pick resource we can reach first; slight bias to corners to reduce symmetry
    best = None
    best_key = None
    for (rx, ry) in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        lead = do - ds  # positive means we're closer
        corner_bias = min(rx, w - 1 - rx) + min(ry, h - 1 - ry)
        key = (-(lead), ds, corner_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def score_step(nx, ny):
        # prefer lowering our distance; penalize moving into/near obstacles
        d0 = man(sx, sy, tx, ty)
        d1 = man(nx, ny, tx, ty)
        delta = d0 - d1
        obs_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    obs_pen += 2 if (ax == 0 and ay == 0) else 1
        # also try to keep distance from opponent slightly
        opp_d = man(nx, ny, ox, oy)
        return (-(d1), -obs_pen, -opp_d, -delta, nx, ny)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append(((dx, dy), nx, ny))
    if not candidates:
        return [0, 0]

    best_move = None
    best_step_key = None
    for (dx, dy), nx, ny in candidates:
        sk = score_step(nx, ny)
        if best_step_key is None or sk > best_step_key:
            best_step_key = sk
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]