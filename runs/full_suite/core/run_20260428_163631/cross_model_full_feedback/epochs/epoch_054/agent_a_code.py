def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b):
        ax, ay = a; bx, by = b
        return abs(ax - bx) + abs(ay - by)

    if resources:
        best = None
        for dx, dy, nx, ny in legal:
            nxt = (nx, ny)
            rd = min(man(nxt, r) for r in resources)
            od = man(nxt, (ox, oy))
            score = rd * 100 - od
            cand = (score, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]
    else:
        best = None
        for dx, dy, nx, ny in legal:
            od = man((nx, ny), (ox, oy))
            cand = (od, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]