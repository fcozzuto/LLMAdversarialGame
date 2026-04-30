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
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_target = None
        best_score = -10**18
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer targets closer to us and farther from opponent; add slight tie-break toward nearer resources overall.
            score = (opd - myd) * 1000 - myd * 3
            if score > best_score:
                best_score = score
                best_target = (rx, ry)
        tx, ty = best_target
    else:
        # No visible resources: head to a good area.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        myd_now = cheb(sx, sy, tx, ty)
        opd_after = cheb(ox, oy, tx, ty)
        # Encourage progress toward target; discourage giving opponent a closer route; keep separation.
        val = (myd_now - myd) * 50 + (opd_after - myd) * 2
        # Mild separation from opponent
        val += (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)) * 0.5
        # Deterministic tie-break: prefer lexicographically smaller move list order by value only
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]