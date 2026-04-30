def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    # If no resources, drift deterministically to center-ish while staying away from opponent.
    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            center_bias = abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny)
            away_bias = -man((nx, ny), opp)
            val = (away_bias, -center_bias, nx, ny)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Choose resource that we can reach sooner than opponent (race heuristic).
    best_t = None
    for r in resources:
        md = man(me, r)
        od = man(opp, r)
        race = (od - md, -md, r[0], r[1])
        if best_t is None or race > best_t[0]:
            best_t = (race, r)
    tx, ty = best_t[1]

    # Move one step greedily toward target; tie-break by maximizing opponent distance.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to_t = man((nx, ny), (tx, ty))
        d_to_opp = man((nx, ny), opp)
        # Prefer smaller distance to target; then larger distance to opponent; then lexicographic determinism.
        val = (-d_to_t, d_to_opp, dx, dy)
        if best is None or val > best[0]:
            best = (val, dx, dy)
    return [best[1], best[2]]