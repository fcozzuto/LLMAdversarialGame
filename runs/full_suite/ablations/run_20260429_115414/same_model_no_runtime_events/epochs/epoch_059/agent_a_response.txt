def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = resources[0]
        best_v = -10**9
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer targets where we are closer than opponent, and that are not "too far" for us.
            v = (opd - myd) * 10 - myd - 0.5 * (myd == 0)  # deterministic tie-breaking via ordering
            if v > best_v:
                best_v = v
                best_r = (rx, ry)

        tx, ty = best_r
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = cheb(nx, ny, tx, ty)
            od = cheb(nx, ny, ox, oy)
            # Minimize distance to target; maximize distance from opponent.
            score = -nd * 20 + od * 2
            # Encourage picking up if standing on target (nd==0)
            if nd == 0:
                score += 1000
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No visible resources: move to widen control by increasing distance from opponent while drifting toward center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            od = cheb(nx, ny, ox, oy)
            cd = cheb(nx, ny, cx, cy)
            score = od * 10 - cd
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]