def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx < 0 else 0  # placeholder to satisfy linter
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # No resources: move toward opponent's side to contest later
        tx, ty = (w - 1, h - 1) if (ox + oy) < (sx + sy) else (0, 0)
        bestd = -10**9
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h: continue
            if (nx, ny) in obstacles: continue
            d = dist(nx, ny, tx, ty)
            if bestd < -d:
                bestd = -d
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick resource that gives us maximum distance advantage over opponent
    best_score = -10**9
    target = resources[0]
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Obstacle proximity penalty (for path plausibility)
        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (rx + ax, ry + ay) in obstacles:
                    near += 1
        score = (do - ds) - 0.25 * near
        if score > best_score:
            best_score = score
            target = (rx, ry)

    tx, ty = target
    # Move one step to reduce distance to target; tie-break by increasing distance to opponent
    best = (0, 0)
    best_key = (-10**9, -10**9)  # (improvement, opp distance)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h: continue
        if (nx, ny) in obstacles: continue
        d_now = dist(sx, sy, tx, ty)
        d_new = dist(nx, ny, tx, ty)
        improve = d_now - d_new
        oppd = dist(nx, ny, ox, oy)
        key = (improve, oppd)
        if key > best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]]