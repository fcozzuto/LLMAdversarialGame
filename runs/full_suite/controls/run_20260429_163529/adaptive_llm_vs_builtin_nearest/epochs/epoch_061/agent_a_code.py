def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dy == 0 else (dy if dy >= 0 else -dy)  # fallback, but we'll compute below

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None

    # Tune to chase resources that are "closer to us than to opponent"
    alpha = 0.65  # reward opponent being far from resource

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # If staying is only safe, allow it by comparing normally
        local_best = None
        for rx, ry in resources:
            d_me = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; slight tie-break toward centrality
            central = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
            val = (d_me - alpha * d_op) + 0.03 * central
            if local_best is None or val < local_best:
                local_best = val

        # Small penalty for moving away from any resource overall to prevent drifting
        d_now = min(dist(sx, sy, rx, ry) for rx, ry in resources)
        d_new = min(dist(nx, ny, rx, ry) for rx, ry in resources)
        drift_pen = 0.02 * (d_new - d_now)

        score = local_best + drift_pen
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dxm, dym)

    dxm, dym = best_move
    return [int(dxm), int(dym)]