def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    # If we are on/adjacent to a resource, just keep going toward the closest one.
    def closest_dist(px, py):
        best = 10**9
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if d < best: best = d
        return best if resources else 0

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        edge_pen = 0
        if nx in (0, w - 1) or ny in (0, h - 1):
            edge_pen = 0.12  # slight preference to avoid getting pinned to edges
        # Obstacle proximity penalty (avoid moving next to obstacles)
        prox_pen = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if (tx, ty) in obstacles:
                    prox_pen += 0.06

        # Choose resource that maximizes opponent distance advantage after this move
        move_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # positive means we are closer
            # Strongly prioritize winning steals, then minimize our distance
            score = margin * 8.0 - ds * 1.2
            # Slightly prefer resources that are closer in absolute terms (reduces dithering)
            score -= 0.15 * closest_dist(ox, oy)  # stable baseline
            # Mildly reward target not too far from center to reduce edge trapping
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dist_center = abs(rx - cx) + abs(ry - cy)
            score -= 0.03 * dist_center
            if score > move_best:
                move_best = score

        total = move_best - edge_pen - prox_pen
        # Deterministic tie-break: prefer dx then dy ordering already from legal generation, so use explicit compare
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]