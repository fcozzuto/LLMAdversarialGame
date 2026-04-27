def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    # Candidate moves
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose best target resource deterministically
    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy
    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        # Prefer resources we can reach sooner than opponent; tie-break by coordinates
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        lead = myd - opd
        key = (lead, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        # No resources visible: drift toward opponent to compete for space
        tx, ty = ox, oy
    else:
        tx, ty = best
    # Evaluate candidate next steps
    best_mv = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Manhattan distance after move to target
        nd = dist((nx, ny), (tx, ty))
        # Small bias: if opponent also closer to same target, avoid giving them easy access by keeping distance
        opd_after = dist((ox, oy), (tx, ty))
        score = nd * 10 + (opd_after - dist((ox, oy), (tx, ty)))  # effectively nd*10
        # Prefer moves that approach target and avoid standing still when equal
        if dx == 0 and dy == 0:
            score += 1
        # Add penalty for moving into immediate obstacle-adjacent if possible (lightweight)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_obs += 1
        score += adj_obs
        key = (score, nx, ny)
        if best_score is None or key < (best_score[0], best_score[1], best_score[2]):
            best_score = (score, nx, ny)
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]