def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def center_dist(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = x - cx
        dy = y - cy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Choose the resource that maximizes our advantage at this next position
        local_best = -10**18
        local_target_dist = 10**9
        for rx, ry in resources:
            self_d = cheb((nx, ny), (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            margin = opp_d - self_d  # positive => we arrive sooner (or equal)
            # tie-break: prefer closer and more central resources
            cand = margin * 10 - self_d - 0.01 * center_dist(rx, ry)
            if cand > local_best or (cand == local_best and self_d < local_target_dist):
                local_best = cand
                local_target_dist = self_d
        score = local_best + 0.02 * (-(center_dist(nx, ny)))  # slight preference to stay central
        if score > best:
            best = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]