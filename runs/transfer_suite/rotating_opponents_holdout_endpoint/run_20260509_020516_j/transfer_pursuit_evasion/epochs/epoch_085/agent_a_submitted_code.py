def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    try:
        w = int(w)
        h = int(h)
    except Exception:
        w, h = 8, 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = []
    for it in observation.get("resources") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))
        except Exception:
            pass

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if targets:
            dres = 10**9
            for tx, ty in targets:
                d = cheb(nx, ny, tx, ty)
                if d < dres:
                    dres = d
            # Prefer closer resources, and keep/attack depending on role
            if is_evader:
                val = -dres + 0.05 * cheb(nx, ny, ox, oy)
            else:
                val = -dres + 0.05 * (-cheb(nx, ny, ox, oy))
        else:
            # No known resources: move to advantage vs opponent
            if is_evader:
                val = cheb(nx, ny, ox, oy)
            else:
                val = -cheb(nx, ny, ox, oy)

        # Deterministic tie-breaker: prefer higher val, then fixed move order (as iterated)
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best

    # Fallback: must return a valid move; try staying if possible
    if inb(sx, sy) and (sx, sy) not in obstacles:
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]