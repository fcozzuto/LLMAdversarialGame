def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_dist(stx, sty, limit=6):
        INF = 10**9
        dist = {}
        q = [(stx, sty)]
        dist[(stx, sty)] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[(x, y)]
            if d >= limit: 
                continue
            for dx, dy in cand:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and (nx, ny) not in dist:
                    dist[(nx, ny)] = d + 1
                    q.append((nx, ny))
        return dist

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny): return [dx, dy]
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if valid(nx, ny): return [mx, my]
        return [0, 0]

    self_dist = bfs_dist(sx, sy, limit=6)
    opp_dist = bfs_dist(ox, oy, limit=6)

    def best_target_score(cell):
        sd = self_dist.get(tuple(cell), 10**7)
        od = opp_dist.get(tuple(cell), 10**7)
        return (sd - od, sd)

    targets = sorted(resources, key=best_target_score)
    target = targets[0]

    tx, ty = target[0], target[1]

    best_move = (0, 0)
    best_val = (10**8, 10**8, 10**8)

    # If we're already on a resource, prioritize staying (deterministic).
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        # one-step greedy: use current dist maps for remaining distance, plus tie-break by moving toward target
        sd = self_dist.get((nx, ny), 10**7) + abs(nx - tx) + abs(ny - ty)
        od = opp_dist.get((tx, ty), 10**7)  # opponent timing proxy for target
        # Also encourage progress directly toward target for robustness against dist-limit misses
        prog = abs(nx - tx) + abs(ny - ty)
        val = (sd - od, prog, sd)
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]