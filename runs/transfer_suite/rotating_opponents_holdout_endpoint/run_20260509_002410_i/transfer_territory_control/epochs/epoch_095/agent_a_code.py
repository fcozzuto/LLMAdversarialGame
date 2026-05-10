def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))

    def man(a, b, c, d):
        v = a - c
        if v < 0: v = -v
        u = b - d
        if u < 0: u = -u
        return v + u

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: man(sx, sy, t[0], t[1]))
    else:
        tx, ty = ox, oy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (-(10**9), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        avoid = -man(nx, ny, ox, oy) * 0.01
        bonus = 0
        if unclaimed and (nx, ny) in unclaimed:
            bonus = 1
        score = -d + avoid + bonus
        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]