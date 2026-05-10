def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    self_pos = (sx, sy)
    self_terr = set(tuple(p) for p in observation.get("self_territory") or [])
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory") or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells") or [])

    # Prefer cells adjacent to our territory (frontier expansion); otherwise unclaimed; else opponent territory.
    frontier = set()
    for (x, y) in self_terr:
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_terr:
                frontier.add((nx, ny))
    targets = sorted(frontier & (unclaimed | opp_terr))
    if not targets:
        targets = sorted(frontier & unclaimed)
    if not targets:
        targets = sorted(unclaimed)
    if not targets:
        targets = sorted(opp_terr)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = [0, 0]
    best_val = -10**9
    neigh_dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            val = -10**6 + (-dist((sx, sy), targets[0]) if targets else 0)
        else:
            cell = (nx, ny)
            val = 0.0
            if cell in opp_terr:
                val += 3.25
            if cell in unclaimed:
                val += 2.25
            if cell in self_terr:
                val += 0.5

            # Additional value for being closer to the nearest target (frontier/opponent/unclaimed).
            if targets:
                dn = min(dist(cell, t) for t in targets)
                val += 1.25 * (-dn)
            else:
                # If no known target, just avoid opponent adjacency less aggressively.
                if opp_terr:
                    dmin = min(dist(cell, ot) for ot in opp_terr)
                    val += 0.2 * (-dmin)

            # If moving away from any frontier cell, slightly penalize; moving into adjacency to frontier helps.
            adj_frontier = 0
            for ddx, ddy in neigh_dirs:
                ax, ay = nx + ddx, ny + ddy
                if inside(ax, ay) and (ax, ay) in unclaimed:
                    adj_frontier += 1
            val += 0.35 * adj_frontier

            # Small deterministic tie-break favoring orthogonal/center moves by order.
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]