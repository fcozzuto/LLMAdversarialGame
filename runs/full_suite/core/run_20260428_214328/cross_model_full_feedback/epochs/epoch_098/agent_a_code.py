def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    me = (sx, sy)
    opp = (ox, oy)

    # Pick a contestable target: high opponent delay relative to our distance, but we must still be reasonably close.
    target = None
    best = None
    if resources:
        for r in resources:
            rd = cheb(me, r)
            od = cheb(opp, r)
            score = (od - rd) * 4 - rd  # prioritize race advantage, break ties by closeness
            tie = 1 if best is not None else 0
            if best is None or score > best or (score == best and (r[0], r[1]) < (target[0], target[1])):
                best = score
                target = r
    else:
        target = (w // 2, h // 2)

    tx, ty = int(target[0]), int(target[1])

    # Choose move that reduces our distance to target, while avoiding obstacles.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        d = cheb((nx, ny), (tx, ty))
        od = cheb((ox, oy), (tx, ty))
        # add a small term to keep pressure if we're already close
        val = (d, -od)  # minimize our distance; prefer larger opponent distance tie-break via -od
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if best_val is None:
        # If boxed in by obstacles, take the least-bad valid step (or stay).
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            d = cheb((nx, ny), (tx, ty))
            if best_val is None or d < best_val:
                best_val = d
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]