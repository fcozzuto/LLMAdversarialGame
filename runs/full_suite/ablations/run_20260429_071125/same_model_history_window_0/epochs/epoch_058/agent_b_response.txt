def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a strategic target resource: prefer where we are closer than opponent.
    best_res = None
    best_val = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        val = (do - ds) * 3 - ds  # strong bias to resources we reach first
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    # If no resources exist, head toward board center deterministically.
    if best_res is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_res

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary objective: reduce distance to target.
        d_now = cheb(sx, sy, tx, ty)
        d_next = cheb(nx, ny, tx, ty)
        score = (d_now - d_next) * 5

        # If landing on a resource, prioritize strongly.
        if (nx, ny) in obstacles:
            score -= 1000
        if (nx, ny) in set((r[0], r[1]) for r in resources):
            score += 500

        # Secondary objective: deny opponent progress.
        if resources:
            do_next = cheb(ox, oy, tx, ty)
            # approximate relative pressure
            score += (d_now - do_next) * 0.2
            score += (-d_next) * 0.05

        # Deterministic tie-break: prefer moves with smallest (dx,dy) lexicographically after score.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]