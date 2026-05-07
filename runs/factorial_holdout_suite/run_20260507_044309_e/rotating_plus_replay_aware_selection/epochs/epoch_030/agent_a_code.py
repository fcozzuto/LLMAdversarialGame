def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if observation.get("environment_name") != "resource_collection":
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def step_toward(tx, ty):
        best = None
        bestd = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0 and len(resources) == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                d = cheb(nx, ny, tx, ty)
                # Prefer reducing our distance; tie-break by staying ahead of opponent
                lead = cheb(ox, oy, tx, ty) - d
                val = lead * 1000 - d
                if val > bestd:
                    bestd, best = val, (dx, dy)
        return best if best is not None else (0, 0)

    best_target = None
    best_score = -10**18
    # If no resources, drift toward center
    if not resources:
        tx, ty = w // 2, h // 2
        return list(step_toward(tx, ty))

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        # Favor resources that we can reach earlier; penalize far ones, mild center bias
        center = cheb(rx, ry, w // 2, h // 2)
        score = lead * 1000 - ds * 6 - center
        if score > best_score:
            best_score, best_target = score, (rx, ry)

    tx, ty = best_target
    dx, dy = step_toward(tx, ty)

    # If we can't make progress (blocked), try a deterministic lateral/vertical alternative
    if dx == 0 and dy == 0:
        prefs = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        for adx, ady in prefs:
            nx, ny = sx + adx, sy + ady
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [adx, ady]
        return [0, 0]

    return [int(dx), int(dy)]