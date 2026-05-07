def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Prefer targets where we arrive sooner than opponent; break ties by being closer.
    best = resources[0]
    best_key = None
    for rx, ry in resources:
        my = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - my, -my, -(abs(rx - sx) + abs(ry - sy)), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Deterministic move preference (fixed order), minimize distance after move and maximize contest.
    deltas = [
        (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (1, -1), (-1, 1), (1, 1)
    ]

    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    best_move = valid[0]
    best_mkey = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my2 = cheb(nx, ny, tx, ty)
        op2 = cheb(ox, oy, tx, ty)
        # Prefer smaller distance to target; if equal, prefer being the earlier collector (op2 - my2 larger).
        mkey = (-(my2), op2 - my2, dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]