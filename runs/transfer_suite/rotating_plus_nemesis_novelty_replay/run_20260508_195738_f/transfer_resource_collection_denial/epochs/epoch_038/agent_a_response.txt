def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    tr = int(observation.get("turn_index", 0))
    rem = int(observation.get("remaining_resource_count", len(resources)))

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # move to farthest corner from opponent while staying valid
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestc = None
        bestv = None
        for cx, cy in corners:
            v = (manh(ox, oy, cx, cy), -(manh(sx, sy, cx, cy)))
            if bestv is None or v > bestv:
                bestv = v
                bestc = (cx, cy)
        tx, ty = bestc
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy):
            return [dx, dy]
        if inb(sx + dx, sy):
            return [dx, 0]
        if inb(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    # Choose competitive target: prioritize we arrive earlier, then deny by being close even if slower.
    best = None
    best_score = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # advantage: positive when we are faster
        adv = do - ds
        # encourage finishing soon and blocking crowded tail late game
        crowd = (ds + do)  # smaller means both are near: good to contest
        # deterministic tie-breaker uses position and turn
        tie = (rx * 31 + ry * 17 + tr) % 1000
        score = adv * 100 + (40 - ds) + (20 - crowd) + (10 if ds == 0 else 0) + (-tie / 1000.0)
        # If equal arrival, prefer slightly longer for opponent (deny).
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best
    # If we are at/adjacent, try to keep pressure: move toward target; otherwise contest.
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestd = None
    bestk = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = manh(nx, ny, tx, ty)
        d_opp_next = manh(ox, oy, tx, ty)
        # For denominator stability, compute a quick "risk": how quickly opponent could also be closer after our move.
        risk = (d_opp_next - d_self)
        key = (-(d_self), risk, rem, -((nx * 13 + ny * 7 + tr) % 97))
        if bestk is None or key > bestk:
            bestk = key
            bestd = (dx, dy)
    if bestd is None:
        return [0, 0]
    return [int(bestd[0]), int(bestd[1])]