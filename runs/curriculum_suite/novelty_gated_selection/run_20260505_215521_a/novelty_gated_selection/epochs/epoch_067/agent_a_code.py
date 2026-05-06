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

    best_move = None
    best_val = -10**18

    if res:
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = -cheb(nx, ny, ox, oy) * 0.01
            best_target = -10**18
            for rx, ry in res:
                self_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                margin = opp_d - self_d  # positive means we're closer than opponent
                cand = margin * 1000 - self_d - cheb(nx, ny, ox, oy) * 0.001
                if cand > best_target:
                    best_target = cand
            val += best_target
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # No resources: try to move closer to opponent deterministically while avoiding obstacles
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = -cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]