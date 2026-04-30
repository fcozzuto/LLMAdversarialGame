def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    if resources:
        best_t = resources[0]
        best_val = -10**18
        for t in resources:
            d_me = md(me, t)
            d_opp = md(opp, t)
            val = (d_opp - d_me) * 10 - d_me
            if val > best_val:
                best_val = val
                best_t = t
    else:
        best_t = opp

    tx, ty = best_t
    legal_sorted = sorted(legal)
    best_move = legal_sorted[0]
    best_dist = 10**18
    for dx, dy in legal_sorted:
        nx, ny = sx + dx, sy + dy
        d = abs(nx - tx) + abs(ny - ty)
        if d < best_dist:
            best_dist = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]