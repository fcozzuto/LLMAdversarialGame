def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def man(a, b, c, d): return abs(a - c) + abs(b - d)
    def cheb(a, b, c, d):
        dx, dy = abs(a - c), abs(b - d)
        return dx if dx > dy else dy

    # Pick a resource where we are earlier than the opponent; if tie, prefer nearer.
    best = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = sd - od  # negative => we arrive earlier
        v = (adv, sd, -man(ox, oy, tx, ty), tx, ty)
        if best is None or v < best[0]:
            best = (v, (tx, ty))
    _, (tx, ty) = best

    # Step selection: obstacle-safe greedy that reduces time-to-target and (slightly) increases opponent time.
    cur_t = cheb(sx, sy, tx, ty)
    cur_o = cheb(ox, oy, tx, ty)
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny): 
            continue
        t = cheb(nx, ny, tx, ty)
        o = cheb(ox, oy, tx, ty)
        # tie-breakers: prefer lowering both, avoid "stall" unless forced, deterministic by coords
        v = (t, cur_t - t, -(o - cur_o), - (dx == 0 and dy == 0), nx, ny, dx, dy)
        if bestm is None or v < bestm[0]:
            bestm = (v, [dx, dy])

    if bestm is not None:
        return bestm[1]

    # Fallback if somehow stuck
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
    return [0, 0]