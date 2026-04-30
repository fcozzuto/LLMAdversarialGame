def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue

        # Defensive positioning against obstacles: prefer fewer adjacent obstacle cells.
        adj_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    adj_obs += 1

        sc = 0
        # Aggressive resource capture: maximize our advantage over opponent for each resource.
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds == 0:
                sc += 10**7
                continue
            # If we can reach earlier, strongly prefer; if not, penalize less to still move toward contests.
            adv = do - ds
            sc += adv * 200 - ds * 3
            # Encourage focusing: higher priority on closer resources.
            sc += (1 if adv > 0 else 0) * max(0, 12 - ds)

        # If no resources in view, default to moving toward center.
        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            sc = -cheb(nx, ny, tx, ty) - adj_obs * 5

        # Opponent pressure: lightly prefer moves that increase our distance to opponent when no immediate gain.
        if resources:
            sc -= max(0, 3 - cheb(nx, ny, ox, oy)) * 5
        sc -= adj_obs * 7

        if sc > best:
            best = sc
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]