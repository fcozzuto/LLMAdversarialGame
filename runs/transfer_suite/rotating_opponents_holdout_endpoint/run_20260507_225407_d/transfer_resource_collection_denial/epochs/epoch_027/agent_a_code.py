def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestd, bestmv = None, [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, cx, cy)
            if bestd is None or d < bestd:
                bestd, bestmv = d, [dx, dy]
        return bestmv

    opp_w = 1.4
    bestv, bestm = None, [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Penalize being adjacent to obstacles
        near_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if (nx + adx, ny + ady) in obs:
                    near_obs += 1
        # Evaluate best resource for this move
        val = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # lower is better: prioritize self reach, then deny opponent
            score = sd - opp_w * od
            if val is None or score < val:
                val = score
        if val is None:
            continue
        total = val + near_obs * 0.8
        if bestv is None or total < bestv:
            bestv, bestm = total, [dx, dy]
    return bestm