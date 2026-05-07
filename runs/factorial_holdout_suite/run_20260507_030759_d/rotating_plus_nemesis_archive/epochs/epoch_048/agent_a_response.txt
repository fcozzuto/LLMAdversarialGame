def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]
    if (sx, sy) in obst:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Two-stage preference: if we can reach no slower, take nearest among them.
        behind = 1 if sd > od else 0
        # Tie-break: maximize margin (opponent further) and prefer smaller sd.
        margin = od - sd
        tie = (tx * 131 + ty * 17) % 997
        key = (behind, sd, -margin, -tie)
        if best is None or key < best_key:
            best = (tx, ty)
            best_key = key

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obst:
        # Deterministically try alternate axis step that reduces distance.
        cand = []
        if dx != 0:
            cand.append((0, 1 if ty > sy else -1))
            cand.append((0, 0))
        if dy != 0:
            cand.append((1 if tx > sx else -1, 0))
            cand.append((0, 0))
        # Keep within grid if possible; otherwise stay.
        best_sd = None
        best_move = (0, 0)
        for adx, ady in cand:
            px, py = sx + adx, sy + ady
            if not (0 <= px < w and 0 <= py < h): 
                continue
            if (px, py) in obst:
                continue
            ns = cheb(px, py, tx, ty)
            if best_sd is None or ns < best_sd or (ns == best_sd and (adx, ady) < best_move):
                best_sd = ns
                best_move = (adx, ady)
        return [int(best_move[0]), int(best_move[1])]

    return [int(dx), int(dy)]