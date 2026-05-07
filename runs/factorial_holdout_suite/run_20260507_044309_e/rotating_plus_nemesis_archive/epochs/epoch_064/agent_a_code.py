def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da >= db else db

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    def min_dist(px, py):
        md = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < md:
                md = d
        return md

    # Precompute for current positions
    my_d0 = min_dist(sx, sy)
    op_d0 = min_dist(ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = min_dist(nx, ny)
        # Deny: consider how quickly opponent could reach the closest remaining resource vs us
        # Also keep them farther from their closest resource.
        op_d = op_d0
        if resources:
            op_d = min(cheb(ox, oy, rx, ry) for (rx, ry) in resources)

        score = 0
        # primary: reduce our distance to nearest resource
        score += (my_d0 - my_d) * 100
        # secondary: if we don't improve, still prefer getting closer
        score += (-my_d) * 2
        # tertiary: deny by pushing ourselves to be closer than opponent (even if opponent next move not simulated)
        score += (op_d - my_d) * 3
        # keep deterministic tie-breaker
        score += (dx * 0.01 + dy * 0.001)

        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]