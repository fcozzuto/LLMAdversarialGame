def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))

    obs = set()
    for x, y in obstacles:
        obs.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Filter reachable-looking resource cells (not on obstacles).
    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid.append((x, y))
    if not valid:
        # Move towards opponent to deny? but keep simple: toward center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        return [dx, dy]

    # Score resources: prefer those we reach no later than opponent; otherwise next closest we can.
    best = None
    best_val = -10**18
    for rx, ry in valid:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Earlier arrival dominates; relative advantage dominates; tie-break by closer to us.
        # If late game, favor immediate pickups.
        urgency = 1
        if tr > 0:
            urgency = 2 if tr <= 8 else 1
        val = (do - ds) * 100000 * urgency + (-ds) * (1000 if tr > 0 else 1) - (0 if rx == sx else 0)
        if val > best_val:
            best_val = val
            best = (rx, ry, ds, do)

    rx, ry, _, _ = best
    # Step greedily in chebyshev metric.
    mx = 0 if rx == sx else (1 if rx > sx else -1)
    my = 0 if ry == sy else (1 if ry > sy else -1)

    nx, ny = sx + mx, sy + my
    # If target step lands on obstacle or out of bounds, try axis-aligned alternatives deterministically.
    if not inb(nx, ny) or (nx, ny) in obs:
        candidates = []
        candidates.append((mx, 0))
        candidates.append((0, my))
        candidates.append((mx, my))
        candidates.append((0, 0))
        for dx, dy in candidates:
            tx, ty = sx + dx, sy + dy
            if inb(tx, ty) and (tx, ty) not in obs:
                return [int(dx), int(dy)]
        return [0, 0]
    return [int(mx), int(my)]