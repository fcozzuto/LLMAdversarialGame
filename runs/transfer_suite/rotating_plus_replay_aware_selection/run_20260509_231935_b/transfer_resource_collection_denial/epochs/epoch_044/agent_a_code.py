def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    res = {(p[0], p[1]) for p in resources}
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Immediate pickup
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            return [dx, dy]

    if not resources:
        return [0, 0]

    # Greedy: pick move that makes us arrive first / closest to high-value contested resources
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_best = 10**9
        opp_best = 10**9
        score = 0
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            md = dist8(nx, ny, rx, ry)
            od = dist8(ox, oy, rx, ry)
            # Prefer resources where we are earlier; strongly penalize where opponent is earlier
            gap = od - md  # positive => we arrive sooner
            # Tie-break via closer resource and avoiding very late grabs
            v = 10 * gap - md
            if md < my_best:
                my_best = md
            if od < opp_best:
                opp_best = od
            score += v
        # Normalize a bit by total resources to reduce extremes
        val = score / float(len(res)) if res else -10**18
        # Small preference for staying if already in a good region
        if (nx, ny) == (sx, sy):
            val += 0.2
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move