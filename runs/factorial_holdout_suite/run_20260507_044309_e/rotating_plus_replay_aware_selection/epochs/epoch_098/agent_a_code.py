def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    env = observation.get("environment_name", "resource_collection")

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def greedy_step(tx, ty):
        # try the move that minimizes our distance to target; deterministic tie-break
        best = None
        cand = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    if env != "resource_collection" or not resources:
        tx, ty = w // 2, h // 2
        return greedy_step(tx, ty)

    # Contest if opponent is significantly closer to any resource
    best_r = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        # heuristic: strongly prefer being closer; if opponent closer by >=1, mark as contest
        if do - ds >= 1:
            val = (1, -(do - ds), ds, rx, ry)  # contest mode
        else:
            val = (0, -adv, ds, rx, ry)       # exploit mode
        if best_r is None or val < best_r[0]:
            best_r = (val, rx, ry, ds, do)

    _, tx, ty, _, _ = best_r
    # one-step safety: if target is unreachable next step due to obstacles, still use greedy_step (it avoids illegal)
    return greedy_step(tx, ty)