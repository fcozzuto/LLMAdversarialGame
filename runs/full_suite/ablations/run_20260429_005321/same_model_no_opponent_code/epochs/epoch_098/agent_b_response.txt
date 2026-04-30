def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def target_score(tx, ty):
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        if myd == 0:
            return 10**9
        # Prefer resources opponent is relatively farther from, then closer to me.
        return (opd - myd) * 20 - myd

    if resources:
        best_t = None
        best_s = -10**18
        for tx, ty in resources:
            s = target_score(tx, ty)
            if s > best_s:
                best_s = s
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Tie-break: don't move into "tight" regions near obstacles; slightly avoid approaching opponent.
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    near_obs += 1
        avoid_op = -cheb(nx, ny, ox, oy) * 0.5
        val = (opd - myd) * 20 - myd * 2 - near_obs * 3 + avoid_op
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]