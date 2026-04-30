def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = (0, h - 1) if (sx + sy) % 2 == 0 else (w - 1, 0)
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            v = -man((nx, ny), (tx, ty)) + 0.05 * man((ox, oy), (nx, ny))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Choose a resource we can reach earlier than the opponent; otherwise choose the best available fallback.
    best_t = resources[0]
    best_s = -10**18
    for t in resources:
        ds = man((sx, sy), t)
        do = man((ox, oy), t)
        # Favor resources closer to us and also slightly farther from opponent (gap-based).
        s = (do - ds) * 10 - ds + 0.1 * (w + h - t[0] - t[1])
        if s > best_s:
            best_s = s
            best_t = t

    tx, ty = best_t
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        ns = man((nx, ny), (tx, ty))
        sep = man((ox, oy), (nx, ny))
        # Primary: decrease distance to target; Secondary: keep separation from opponent; Tertiary: avoid moving "away" too much.
        v = -ns * 100 + sep - (abs(dx) + abs(dy)) * 0.01
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best