def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Evaluate candidate destination resources by "win probability" proxy: (opp_dist - self_dist),
    # plus a small preference for nearer resources to reduce dithering.
    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        val = (od - sd) * 100 - sd
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    rx, ry = best_r

    # Greedy step toward (rx,ry), but if a step is blocked/invalid, fall back to best among legal steps.
    tx = 0 if rx == sx else (1 if rx > sx else -1)
    ty = 0 if ry == sy else (1 if ry > sy else -1)
    pref = (tx, ty)

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return False
        if (nx, ny) in blocked:
            return False
        return True

    # First try preferred direct move if it changes our distance and doesn't go into obstacles.
    if pref in moves and pref != (0, 0) and legal(pref[0], pref[1]):
        nx, ny = sx + pref[0], sy + pref[1]
        if kdist(nx, ny, rx, ry) < kdist(sx, sy, rx, ry):
            return [pref[0], pref[1]]

    # Otherwise, pick the move maximizing advantage over opponent for the chosen target resource,
    # with tie-breaker favoring progress and minimal step-cost.
    best_m = (0, 0)
    best_mv = -10**18
    for dx, dy in moves:
        if not legal(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        sd2 = kdist(nx, ny, rx, ry)
        od2 = kdist(ox, oy, rx, ry)
        adv = od2 - sd2
        # If we moved, prefer larger adv; then prefer smaller remaining distance; then prefer non-stay.
        mv = adv * 100 - sd2 * 3 - (0 if (dx, dy) == (0, 0) else 1)
        if mv > best_mv:
            best_mv = mv
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]