def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_score = None
    for rx, ry in res:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # If we can arrive no later, prioritize advantage. If not, choose where opponent is farthest (denial).
        if myd <= opd:
            sc = 10000 + (opd - myd) * 50 - myd
        else:
            sc = (opd * -200) + myd * 5 - (myd - opd)
        if best is None or sc > best_score or (sc == best_score and (rx, ry) < best):
            best = (rx, ry)
            best_score = sc

    tx, ty = best
    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    candidates = []
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                candidates.append((manh(nx, ny, tx, ty), -abs(dx) - abs(dy), dx, dy))
    candidates.sort(reverse=False)
    if not candidates:
        return [0, 0]
    # Tie-break deterministically toward smaller dx then smaller dy to be stable.
    best_c = None
    for dist, _, dx, dy in candidates:
        key = (dist, abs(dx), abs(dy), dx, dy)
        if best_c is None or key < best_c[0]:
            best_c = (key, [dx, dy])
    return best_c[1]