def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    try:
        w = int(w)
        h = int(h)
    except:
        return [0, 0]
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    turn = observation.get("turn_index", 0)
    try:
        turn = int(turn)
    except:
        turn = 0

    best = None
    best_val = -10**18
    if res:
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            move_best = -10**18
            for rx, ry in res:
                dS = cheb(nx, ny, rx, ry)
                dO = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent; lightly penalize distance.
                val = (dO - dS) - 0.01 * dS
                if val > move_best:
                    move_best = val
            # Small deterministic tie-break toward moves that keep us closer to opponent's likely contest.
            tie = -0.001 * cheb(nx, ny, ox, oy)
            val = move_best + tie + (0.0000001 * ((turn + dx + 2*dy) % 2))
            if val > best_val:
                best_val = val
                best = (dx, dy)
    else:
        # No visible resources: drift to reduce chebyshev distance to opponent (encourages block/contest).
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = -cheb(nx, ny, ox, oy) + 0.0000001 * ((turn + dx + 2*dy) % 2)
            if val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]