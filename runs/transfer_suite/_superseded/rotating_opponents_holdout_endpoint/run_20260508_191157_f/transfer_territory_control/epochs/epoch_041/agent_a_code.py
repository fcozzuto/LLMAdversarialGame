def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    corners = {(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)}

    targets = []
    for c in observation.get("unclaimed_cells") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                targets.append((x, y))
    if not targets:
        for c in observation.get("resources") or []:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if 0 <= x < w and 0 <= y < h:
                    targets.append((x, y))
    if not targets:
        for c in corners:
            if c not in blocked:
                targets.append(c)
    if not targets:
        return [0, 0]

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    def d2(a, b, c, e):
        dx, dy = a - c, b - e
        return dx * dx + dy * dy

    best = (10**18, 0, 0)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        penalty = 0
        if (nx, ny) in self_t:
            penalty += 50
        if (nx, ny) in opp_t:
            penalty += 20
        nt = 10**18
        for tx, ty in targets[:30]:
            val = d2(nx, ny, tx, ty) + 0.25 * d2(nx, ny, ox, oy)
            if val < nt:
                nt = val
        sc = nt + penalty
        if sc < best[0]:
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]