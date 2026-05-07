def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Estimate opponent target using a simple race heuristic.
    best_opp = None
    best_opp_val = None
    for rx, ry in resources:
        od = manh(ox, oy, rx, ry)
        sd = manh(sx, sy, rx, ry)
        # Prefer what opponent can reach quickly and what we are less likely to take.
        v = (od, sd - od, od - sd)
        if best_opp is None or v < best_opp_val:
            best_opp = (rx, ry)
            best_opp_val = v

    # Choose our target to avoid the opponent's likely pick.
    # Primary: maximize advantage (opp_dist - self_dist); Secondary: be close.
    best = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) == best_opp:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # If we still must fight for same, allow but with penalty.
        v = (-adv, sd, abs((rx - sx) - (ry - sy)))
        if best is None or v < best_val:
            best = (rx, ry)
            best_val = v

    if best is None:
        # Fallback: take best available even if it's the opponent's likely target.
        best = best_opp

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # Deterministic obstacle avoidance: try axis steps in order.
        candidates = []
        if dx != 0:
            candidates.append([dx, 0])
        if dy != 0:
            candidates.append([0, dy])
        candidates.append([0, 0])
        for ddx, ddy in candidates:
            xx, yy = sx + ddx, sy + ddy
            if 0 <= xx < w and 0 <= yy < h and (xx, yy) not in obstacles:
                return [int(ddx), int(ddy)]
        return [0, 0]

    return [int(dx), int(dy)]