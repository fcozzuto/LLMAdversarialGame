def choose_move(observation):
    def ti(v):
        try:
            return int(v)
        except:
            return 0

    w = ti(observation.get("grid_width", 8)) or 8
    h = ti(observation.get("grid_height", 8)) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = ti(sp[0]), ti(sp[1])
    ox, oy = ti(op[0]), ti(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        x = y = None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
        elif isinstance(p, dict) and "x" in p and "y" in p:
            x, y = ti(p.get("x")), ti(p.get("y"))
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        x = y = None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = ti(r.get("x")), ti(r.get("y"))
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    # Choose a target we can reach no later than opponent; if tie, go closer.
    best = None
    best_key = None
    for rx, ry in res:
        dS = md(sx, sy, rx, ry)
        dO = md(ox, oy, rx, ry)
        key = (dS - dO, dS, rx, ry)  # maximize "advantage" -> minimize (dS-dO)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Evaluate one-step move: maximize (opponent distance advantage) while reducing our distance.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dS2 = md(nx, ny, tx, ty)
        dO2 = md(ox, oy, tx, ty)
        score = (dO2 - dS2, -dS2, -abs(tx - nx) - abs(ty - ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        # All candidate steps blocked; allow staying.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]