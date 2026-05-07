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
    best_sc = None
    for rx, ry in res:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # Prefer resources where we arrive earlier; otherwise deny by targeting farthest-from-opponent.
        if myd <= opd:
            sc = 100000 + (opd - myd) * 300 - myd
        else:
            sc = (opd - myd) * 50 - myd * 3
        # Mild tie-break: prefer alignment/closer to our axis progress.
        sc += -abs((rx - sx)) * 0.5 - abs((ry - sy)) * 0.5
        if best is None or sc > best_sc or (sc == best_sc and (rx, ry) < best):
            best_sc = sc
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # If direct step goes into obstacle, fall back to best non-obstacle among 9 moves.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obs:
        candidates = []
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                tx, ty = sx + ddx, sy + ddy
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                    myd = manh(tx, ty, rx, ry)
                    opd = manh(tx, ty, ox, oy)
                    if myd <= opd:
                        sc = 100000 + (opd - myd) * 300 - myd
                    else:
                        sc = (opd - myd) * 50 - myd * 3
                    candidates.append((sc, ddx, ddy))
        if candidates:
            candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
            return [int(candidates[0][1]), int(candidates[0][2])]
        return [0, 0]

    return [int(dx), int(dy)]