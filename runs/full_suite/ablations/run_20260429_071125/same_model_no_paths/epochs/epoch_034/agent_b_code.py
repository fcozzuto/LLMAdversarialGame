def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = [(dx, dy) for dx, dy in moves if ok(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    best = None
    if resources:
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            md = None
            for rx, ry in resources:
                d = abs(rx - nx)
                e = abs(ry - ny)
                dist = d if d > e else e
                if md is None or dist < md:
                    md = dist
            cand = (md, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    # No resources: move to reduce Chebyshev distance to opponent (deterministic)
    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d = abs(ox - nx)
        e = abs(oy - ny)
        dist = d if d > e else e
        cand = (dist, dx, dy)
        if best is None or cand < best:
            best = cand
    return [best[1], best[2]]