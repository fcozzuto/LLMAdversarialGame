def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y): obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y) and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # Choose a target resource using my closeness vs opponent, with deterministic tie-breaks
    if res:
        best = None
        best_key = None
        for rx, ry in res:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - md  # positive means I'm closer
            # Encourage gaps, then quicker overall, then prefer "lower" coords deterministically
            key = (gap, -md, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: drift toward center but keep away from opponent
        tx, ty = (w // 2, h // 2)

    # Decide whether to chase or flee depending on who is closer to the target
    my_d = cheb(sx, sy, tx, ty)
    op_d = cheb(ox, oy, tx, ty)
    flee = (op_d <= my_d) or (cheb(sx, sy, ox, oy) <= 2)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        if flee:
            score = (cheb(nx, ny, ox, oy), -cheb(nx, ny, tx, ty))
        else:
            score = (-cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), -abs(nx - tx) - abs(ny - ty))
        # Deterministic tie-break: smallest dx, then smallest dy, then position order
        candidates.append((score, -dx, -dy, nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    dx, dy = candidates[0][5], candidates[0][6]
    return [int(dx), int(dy)]