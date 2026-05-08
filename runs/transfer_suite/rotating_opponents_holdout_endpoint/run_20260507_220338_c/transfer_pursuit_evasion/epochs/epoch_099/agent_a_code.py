def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    tx = 0 if ox == sx else (1 if ox > sx else -1)
    ty = 0 if oy == sy else (1 if oy > sy else -1)
    pref = (tx, ty)

    if ok(sx + pref[0], sy + pref[1]):
        return [pref[0], pref[1]]

    best = None
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist(nx, ny)
        if d < best_d or (d == best_d and (dx, dy) == pref):
            best_d = d
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]