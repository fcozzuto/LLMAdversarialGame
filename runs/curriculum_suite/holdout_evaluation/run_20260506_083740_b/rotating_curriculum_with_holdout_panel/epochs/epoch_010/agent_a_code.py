def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = list(observation.get("resources", []) or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if resources:
        rx, ry = resources[0]
        best = None
        bestd = 10**9
        for r in resources:
            x, y = r
            d = abs(sx - x) + abs(sy - y)
            if d < bestd:
                bestd = d
                rx, ry = x, y
        best = [0, 0]
        best_score = -10**18
        for dx, dy, nx, ny in cand:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(nx - ox) + abs(ny - oy)
            score = (-ds * 10) + do
            if score > best_score:
                best_score = score
                best = [dx, dy]
        return best
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        best_score = -10**18
        for dx, dy, nx, ny in cand:
            ds = abs(nx - cx) + abs(ny - cy)
            do = abs(nx - ox) + abs(ny - oy)
            score = (-ds * 10) + do
            if score > best_score:
                best_score = score
                best = [dx, dy]
        return best