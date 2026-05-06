def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    tpos = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                tpos.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            tpos.append((r[0], r[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not legal(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy)

    best = (None, -10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if not tpos:
            dOpp = dist(nx, ny, ox, oy)
            dCtr = dist(nx, ny, w // 2, h // 2)
            score = (dOpp * 0.01) - (dCtr * 0.001)
        else:
            # Prefer resources where we become closer than opponent.
            score = -10**18
            for rx, ry in tpos:
                d_next = dist(nx, ny, rx, ry)
                d_opp = dist(ox, oy, rx, ry)
                # margin positive => we are closer (or will be closer) than opponent
                margin = d_opp - d_next
                # slight preference for reducing absolute distance
                cand = margin - 0.05 * d_next
                if cand > score:
                    score = cand
            # Mildly avoid getting too close to opponent (safety)
            dOppNow = dist(nx, ny, ox, oy)
            score -= 0.002 * dOppNow

        # Deterministic tie-break: prefer staying? no; prefer smallest dx,dy ordering via iteration order.
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [best[0][0], best[0][1]]