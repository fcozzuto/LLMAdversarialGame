def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]  # list of [x,y]

    # Candidate moves
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]

    # Clamp/validate target metric helpers
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # If no resources, head toward opponent corner deterministically
    if not resources:
        tx = w - 1 if x < w - 1 else 0
        ty = h - 1 if y < h - 1 else 0
        best = None
        bestv = -10**18
        for dxm, dym in moves:
            nx, ny = x + dxm, y + dym
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -d2(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dxm, dym)
        return list(best if best is not None else (0, 0))

    # Score a move by choosing the best resource to pursue and competing with opponent
    best_move = (0, 0)
    best_score = -10**18
    for dxm, dym in moves:
        nx, ny = x + dxm, y + dym
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer immediate resource capture
        immediate = 1 if any(r[0] == nx and r[1] == ny for r in resources) else 0

        # Evaluate best target resource for this candidate
        # Objective: maximize (opp_dist - my_dist) with slight preference for nearer overall
        my_best = -10**18
        for rx, ry in resources:
            md = d2(nx, ny, rx, ry)
            od = d2(ox, oy, rx, ry)
            # If opponent is already very close, deprioritize; if I'm closer, prioritize
            v = (od - md) * 10 - md * 0.001
            if (rx, ry) == (nx, ny):
                v += 1e6
            if v > my_best:
                my_best = v

        # Small tie-break: move towards center-ish deterministically to reduce oscillation
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = d2(nx, ny, cx, cy) * 0.0001

        score = my_best + immediate * 2e6 - center_pen
        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]