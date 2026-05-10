def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    res = {(p[0], p[1]) for p in resources}
    obs = {(p[0], p[1]) for p in obstacles}
    if not resources:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Immediate pickup
    best_adj = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            best_adj = [dx, dy]
            break
    if best_adj is not None:
        return best_adj

    opp_d_cache = {}
    for rx, ry in res:
        if (rx, ry) not in obs:
            opp_d_cache[(rx, ry)] = dist8(ox, oy, rx, ry)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Evaluate based on best contested target from next position
        local_best = -10**18
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            sd = dist8(nx, ny, rx, ry)
            od = opp_d_cache.get((rx, ry), dist8(ox, oy, rx, ry))
            # Prefer targets where we arrive earlier; tie-break toward shorter self distance
            val = (od - sd) * 100 - sd
            if val > local_best:
                local_best = val
        # Small preference to move toward overall resource centroid (deterministic)
        if resources:
            cx = 0
            cy = 0
            for p in resources[:6]:
                cx += p[0]
                cy += p[1]
            cx //= min(6, len(resources))
            cy //= min(6, len(resources))
            centroid_bias = -dist8(nx, ny, cx, cy)
            local_best += centroid_bias
        if local_best > best_val:
            best_val = local_best
            best_move = [dx, dy]

    return best_move