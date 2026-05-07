def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    if resources:
        scored = []
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = (1 if ds <= do else 0)  # prefer resources where we are closer/equal
            scored.append((-(gain), ds, rx, ry))
        scored.sort()
        rx, ry = scored[0][2], scored[0][3]

        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, rx, ry)
            opp = cheb(nx, ny, ox, oy)
            cand = (d, -opp, dx, dy)  # closer to target, also keep away from opponent
            if best is None or cand < best[0]:
                best = (cand, [dx, dy])
        if best is not None:
            return best[1]

    bx = 0 if sx == ox else (-1 if sx > ox else 1)
    by = 0 if sy == oy else (-1 if sy > oy else 1)
    for dx, dy in [(bx, by), (bx, 0), (0, by), (0, 0), (-bx, -by), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]