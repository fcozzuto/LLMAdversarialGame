def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    moves = [(0, 0), (1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            row_bias = 0
            drow = abs(ty - oy)
            if drow == 0: row_bias = -1.8
            elif drow == 1: row_bias = -1.0
            elif drow == 2: row_bias = -0.4
            value = (sd - od * 0.95) + row_bias
            key = (int(value * 1000), sd, tx, ty)  # deterministic tie-break
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        tx, ty = best[1]
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)

        # If diagonal towards target is blocked, take best among remaining legal deltas
        cand = []
        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((mdx, mdy))
        if cand:
            cand.sort(key=lambda md: (
                cheb(sx + md[0], sy + md[1], tx, ty),
                abs(md[0] - dx) + abs(md[1] - dy),
                md[0], md[1]
            ))
            return [int(cand[0][0]), int(cand[0][1])]
        return [0, 0]
    else:
        # No visible resources: head toward the midpoint row/col between agents (good vs sweep_row behavior)
        tx = (sx + ox) // 2
        ty = (sy + oy) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [int(dx), int(dy)]