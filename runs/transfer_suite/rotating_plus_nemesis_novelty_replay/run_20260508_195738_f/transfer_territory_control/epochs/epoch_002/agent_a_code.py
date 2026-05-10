def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set((a[0], a[1]) for a in (observation.get("obstacles", []) or []))
    unclaimed = set((c[0], c[1]) for c in (observation.get("unclaimed_cells", []) or []))
    opp_cells = set((c[0], c[1]) for c in (observation.get("opponent_territory", []) or []))
    self_cells = set((c[0], c[1]) for c in (observation.get("self_territory", []) or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    # Targets: unclaimed first, otherwise try to approach opponent
    if unclaimed:
        targets = list(unclaimed)
    elif opp_cells:
        targets = list(opp_cells)
    else:
        targets = [(ox, oy)]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**9, 10**9, 10**9, 0, 0)
    best_move = (0, 0)

    def clamp_in(ax, ay):
        return 0 <= ax < w and 0 <= ay < h

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not clamp_in(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Determine cell priority
        if (nx, ny) in unclaimed:
            pr = 0
        elif (nx, ny) in opp_cells:
            pr = 1
        elif (nx, ny) in self_cells:
            pr = 2
        else:
            pr = 3

        # Distance to closest good target (prefer unclaimed strongly)
        md = 10**9
        for tx, ty in targets:
            d = cheb(nx, ny, tx, ty)
            if d < md:
                md = d

        # Mild penalty for being adjacent to obstacles (encourage safer routes)
        adj_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            axx, ayy = nx + ax, ny + ay
            if 0 <= axx < w and 0 <= ayy < h and (axx, ayy) in obstacles:
                adj_obs += 1

        # Prefer moves that don't stall unless it's best
        stall = 1 if (dx == 0 and dy == 0) else 0
        cand = (pr, md, adj_obs, stall, (abs(dx) + abs(dy)))
        if cand < best:
            best = cand
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]