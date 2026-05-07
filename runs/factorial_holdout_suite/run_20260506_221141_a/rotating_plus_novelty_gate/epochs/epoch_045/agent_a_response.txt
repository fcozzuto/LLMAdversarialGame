def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def diag_time(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    scored = []
    for rx, ry in res:
        st = diag_time(sx, sy, rx, ry)
        ot = diag_time(ox, oy, rx, ry)
        adv = ot - st
        scored.append((adv, -st, ot, rx, ry))
    scored.sort(reverse=True)
    best = scored[0]

    # If we aren't ahead, switch to denial: pick resource with smallest opponent time, then closest to self.
    if best[0] < 1:
        scored2 = [( -s[2], s[1], s[3], s[4]) for s in scored]  # (-opp_time, -self_time, rx, ry)
        scored2.sort(reverse=True)
        _, _, rx, ry = scored2[0]
        target = (rx, ry)
    else:
        target = (best[3], best[4])

    tx, ty = target

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_step = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        nst = diag_time(nx, ny, tx, ty)
        nother = diag_time(ox, oy, tx, ty) - 0  # constant, keep for stability
        val = (nother - nst, -nst, -(abs(nx - ox) + abs(ny - oy)), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_step = [dx, dy]

    return best_step