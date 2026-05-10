def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If nothing visible, head to the center while keeping distance from opponent
    if not resources:
        cx, cy = w // 2, h // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            v = -dist8(nx, ny, cx, cy) + 0.3 * dist8(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target resource that we can reach earlier than opponent (tie-break by closeness)
    best_t = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        sd = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        score = (od - sd) * 10 - sd
        # slight preference for nearer resources when relative lead is small
        if (od - sd) == 0:
            score -= 0.1 * (sd)
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    rx, ry = best_t

    # Move: choose step that most improves lead to the target; also avoid obstacles (engine would keep in place anyway)
    best_m = (0, 0)
    best_mv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        sd2 = dist8(nx, ny, rx, ry)
        # Predict opponent could also move toward target: approximate by reducing their dist by 1 (but deterministically)
        od2 = dist8(ox, oy, rx, ry)
        approx_lead = od2 - sd2
        v = approx_lead * 10 - sd2
        # small repulsion to prevent oscillating near opponent when lead is tied
        v += 0.05 * dist8(nx, ny, ox, oy)
        if v > best_mv:
            best_mv = v
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]