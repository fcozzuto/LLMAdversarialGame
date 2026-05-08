def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obst:
            # fallback: try axis-aligned
            for adx, ady in [(dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 0)]:
                nx, ny = sx + adx, sy + ady
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                    return [adx, ady]
        return [dx, dy]

    # Pick best "contest target": high lead + reasonable closeness
    best_t = resources[0]
    best_tv = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        tv = (do - ds) - 0.08 * ds
        if tv > best_tv:
            best_tv = tv
            best_t = (rx, ry)
    tx, ty = best_t

    # Score moves by how much they improve our lead to the target,
    # and slightly discourage moving toward squares the opponent can already reach sooner.
    best_move = [0, 0]
    best_mv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        ds_now = cheb(nx, ny, tx, ty)
        ds_cur = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        lead_now = do - ds_now
        lead_cur = do - ds_cur

        # Small anti-denial: avoid stepping closer to a resource where opponent advantage is strong.
        risk = 0
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            if d2 + 0 < d1:  # opponent likely reaches first
                risk += 1
        mv = (lead_now - lead_cur) + 0.6 * lead_now - 0.02 * ds_now - 0.01 * risk
        if mv > best_mv:
            best_mv = mv
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]