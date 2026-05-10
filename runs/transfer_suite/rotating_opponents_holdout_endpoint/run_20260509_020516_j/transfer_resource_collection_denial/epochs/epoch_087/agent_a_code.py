def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = ox, oy
    else:
        # Pick a resource we are likely to reach first (maximize opponent slack), tie-break by nearer and coordinates.
        best = None
        best_key = None
        for rx, ry in resources:
            sd = md((sx, sy), (rx, ry))
            od = md((ox, oy), (rx, ry))
            slack = od - sd
            key = (slack, -sd, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    moves = [(0, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate next step: maximize reduction in (our distance advantage over opponent) toward target.
        our = md((nx, ny), (tx, ty))
        opp = md((ox, oy), (tx, ty))
        adv = opp - our
        # slight repulsion from obstacles if close
        near_pen = 0
        if obstacles:
            for ax, ay in ((nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1)):
                if (ax, ay) in obstacles:
                    near_pen += 1
        val = (adv, -our, -near_pen, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]