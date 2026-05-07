def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    # If we are already on a resource, collect it.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Choose a target that we can steal (positive steal score), otherwise the least bad.
    best = None
    for rx, ry in resources:
        self_d = dist_cheb((sx, sy), (rx, ry))
        opp_d = dist_cheb((ox, oy), (rx, ry))
        steal = opp_d - self_d  # want large positive
        # Tie-break: prefer nearer targets to act quickly; also prefer cells on our side.
        side_bias = (rx + ry) - (sx + sy)
        cand = (steal, -self_d, -abs(side_bias))
        if best is None or cand > best[0]:
            best = (cand, (rx, ry))

    tx, ty = best[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Pick move that best reduces distance to target while also considering denial (avoid walking into opponent advantage).
    bestm = None
    for dx, dy, nx, ny in moves:
        self_to_target = dist_cheb((nx, ny), (tx, ty))
        opp_to_target = dist_cheb((ox, oy), (tx, ty))
        # Higher is better.
        # If opponent is currently closer, prioritize moves that reduce the gap we control.
        gap_after = (opp_to_target - self_to_target)
        # Also encourage not moving away from target.
        progress = -self_to_target
        cand = (gap_after, progress, -(abs(nx - tx) + abs(ny - ty)), -abs(nx - ox) - abs(ny - oy))
        if bestm is None or cand > bestm[0]:
            bestm = (cand, [dx, dy])

    return bestm[1]