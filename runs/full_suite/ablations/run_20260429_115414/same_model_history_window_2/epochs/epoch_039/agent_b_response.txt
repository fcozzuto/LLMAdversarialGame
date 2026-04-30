def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        best_score = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; otherwise still try if close.
            lead = do - ds  # positive is good
            # Add tie-breaks to reduce deterministic flipping: slight bias to nearer overall.
            score = (lead * 10) - ds
            if best is None or score > best_score or (score == best_score and (rx, ry) < best):
                best_score = score
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: go toward center to maximize future capture chances.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # One-step move: choose legal neighbor that reduces distance to target,
    # while discouraging moving adjacent to opponent when not needed.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        ds_old = cheb(sx, sy, tx, ty)
        # Opponent proximity penalty (deterministic, local).
        opp_d = cheb(nx, ny, ox, oy)
        # Prefer progress; tie-break by avoiding getting too close to opponent.
        val = (ds_old - ds_new) * 100 - ds_new
        if opp_d <= 1:
            val -= 200
        # Small deterministic preference: prioritize moves that increase x then y (stable ordering)
        val += (nx - sx) * 0.01 + (ny - sy) * 0.001
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]