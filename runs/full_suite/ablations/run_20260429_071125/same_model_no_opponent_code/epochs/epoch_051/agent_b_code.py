def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def step_penalty(nx, ny):
        # Penalize moving next to opponent to reduce collisions; slight penalty helps stability.
        da = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
        p = 0.0
        if da <= 1:
            p += 0.35
        # Small wall/obstacle proximity penalty
        for ex in (nx - 1, nx, nx + 1):
            for ey in (ny - 1, ny, ny + 1):
                if (ex, ey) in obstacles:
                    p += 0.08
        return p

    if not resources:
        # Deterministic fallback: move toward center while staying away from opponent/obstacles.
        best = None
        for dx, dy, nx, ny in cand:
            val = (abs(nx - cx) + abs(ny - cy)) + step_penalty(nx, ny)
            key = (val, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    best_move = None
    best_key = None
    for dx, dy, nx, ny in cand:
        # Evaluate best resource to pursue from next position.
        local_best = None
        for rx, ry in resources:
            d_self = dist((nx, ny), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # If opponent is closer, steer away a bit unless we can reach much faster.
            val = d_self - 0.55 * d_opp
            # Prefer resources in the general direction away from being trapped: slight center bias.
            val += 0.02 * (abs(rx - cx) + abs(ry - cy))
            if local_best is None or val < local_best[0]:
                local_best = (val, rx, ry)
        target_val = local_best[0]
        # Tie-breaker: prefer increasing distance from opponent (safer collection paths).
        opp_sep = -dist((nx, ny), (ox, oy))
        pen = step_penalty(nx, ny)
        key = (target_val + pen + 0.001 * opp_sep, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move