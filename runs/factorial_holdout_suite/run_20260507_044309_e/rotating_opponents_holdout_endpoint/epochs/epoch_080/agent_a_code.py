def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_target(rx, ry):
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; otherwise minimize our distance and maximize opponent delay.
        return (sd - od, sd, -(rx + ry))

    resources.sort()
    best = None
    best_key = None
    for rx, ry in resources:
        key = score_target(rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # Try direct diagonal/axis step first; then fall back to other steps toward target; then stay.
    candidates.append((dx, dy))
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if (mx, my) == (dx, dy):
                continue
            if mx == 0 and my == 0:
                continue
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # closer (cheb) to target is better; deterministic tie-break by direction
                candidates.append((mx, my))
    candidates.append((0, 0))

    def cand_key(mx, my):
        nx, ny = sx + mx, sy + my
        return (cheb(nx, ny, tx, ty), abs(mx) + abs(my), mx, my)

    best_move = None
    best_ck = None
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            ck = cand_key(mx, my)
            if best_ck is None or ck < best_ck:
                best_ck = ck
                best_move = (mx, my)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]