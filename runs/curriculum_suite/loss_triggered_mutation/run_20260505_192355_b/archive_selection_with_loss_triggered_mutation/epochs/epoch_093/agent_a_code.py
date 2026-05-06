def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < int(w) and 0 <= y < int(h):
                obst.add((x, y))

    w, h = int(w), int(h)
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not resources:
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best = None
    best_move = [0, 0]
    mypos = (sx, sy)
    opp = (ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        npos = (nx, ny)
        mind = 10**9
        for rp in resources:
            d = cheb(npos, rp)
            if d < mind:
                mind = d
        # Prefer getting closer to resources; tie-break by keeping farther from opponent (deterministic).
        oppd = cheb(opp, npos)
        score = (-mind, oppd, dx, dy)
        if best is None or score < best:
            best = score
            best_move = [dx, dy]

    return best_move