def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    if not resources:
        return [0, 0]

    # Pick move maximizing guaranteed advantage heuristic; strongly prefer immediate collections.
    best_move = [0, 0]
    best_score = -10**18

    # Precompute resource counts to keep deterministic order effect minimal.
    # Use stable ordering by (x,y).
    resources_sorted = sorted(resources, key=lambda r: (r[0], r[1]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        score = 0
        # Immediate resource capture
        immediate = None
        for rx, ry in resources_sorted:
            if nx == rx and ny == ry:
                immediate = (rx, ry)
                break
        if immediate is not None:
            # Prefer capturing over anything else; incorporate opponent distance.
            rx, ry = immediate
            score = 10**12 + (cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)) * 100
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
            continue

        # Evaluate best target for this next position.
        local_best = -10**18
        for rx, ry in resources_sorted:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Primary: resources we can reach no later than opponent.
            if myd <= opd:
                # Encourage larger lead, and earlier arrival.
                val = (opd - myd) * 100 - myd
            else:
                # If opponent is closer, de-emphasize but still consider reducing loss.
                val = -(myd - opd) * 30 - myd

            # Secondary: avoid straying toward edges if opponent could contest sooner.
            edge_pen = 0
            if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
                edge_pen = 3
            val -= edge_pen

            if val > local_best:
                local_best = val

        score = local_best
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]