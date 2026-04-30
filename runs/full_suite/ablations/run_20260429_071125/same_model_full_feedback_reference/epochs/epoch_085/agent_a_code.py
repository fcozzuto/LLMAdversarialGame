def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if myd == 0:
            key = (-1000, 0, opd)  # if standing on a resource, take it
        else:
            # Prefer resources I can reach strictly earlier than opponent.
            primary = 0 if myd < opd else 1
            key = (primary, myd, opd, myd - opd)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_mkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        to_target = cheb(nx, ny, tx, ty)
        sep_from_opp = cheb(nx, ny, ox, oy)
        # Deterministic tie-breakers: prefer smaller dx then dy (by tuple ordering)
        mkey = (to_target, -sep_from_opp, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]