def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1 - sx, h - 1 - sy
    else:
        tx, ty = None, None

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_sc = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        if ny < 0: ny = 0
        if nx >= w: nx = w - 1
        if ny >= h: ny = h - 1
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        if not resources:
            sc = -(cheb(nx, ny, tx, ty))
        else:
            # Score by most winnable resource after this step, with tie-breaking by self closeness.
            top = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                margin = opd - myd  # positive => we are sooner
                # Favor: being sooner a lot; then being very close; then considering that opponent is far.
                cand = (margin, -myd, opd)
                if top is None or cand > top:
                    top = cand
            # Convert tuple to scalar for easy comparison (deterministic).
            sc = (top[0] * 1000) + (top[1] * 10) + (-top[2])

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]