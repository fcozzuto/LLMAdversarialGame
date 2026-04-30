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

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    my = (sx, sy); op = (ox, oy)

    if resources:
        best = None
        best_key = None
        for r in resources:
            dmy = cheb(my, r)
            dop = cheb(op, r)
            contested = dmy <= dop
            if contested:
                key = (0, -(dop - dmy), dmy, r[0], r[1])
            else:
                key = (1, (dop - dmy), dmy, r[0], r[1])
            if best_key is None or key < best_key:
                best_key = key; best = r
        target = best
    else:
        target = (sx, sy)

    tset = set(resources)

    def score_move(nx, ny, dx, dy):
        dmy = cheb((nx, ny), target)
        dop = cheb((nx, ny), op)
        gain = 0
        if (nx, ny) == target:
            gain += 1000
        # Prefer not to step into opponent "immediate neighborhood"
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            gain -= 120
        # Balance: get closer to target but stay farther from opponent
        return (-dmy) + 0.8 * dop + gain

    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        sc = score_move(nx, ny, dx, dy)
        if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < best):
            best_score = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]