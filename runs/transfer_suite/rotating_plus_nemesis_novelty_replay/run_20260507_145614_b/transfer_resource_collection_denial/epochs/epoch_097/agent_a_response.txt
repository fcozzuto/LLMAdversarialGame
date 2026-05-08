def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If we're on a resource, stay (engine likely collects automatically; deterministic stop).
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # Opponent sweep: prioritize moving toward the contested row/col towards its direction.
    sweep_row = (oy == sy)
    sweep_col = (ox == sx)

    def best_resource_from(x, y):
        # Choose a resource that we can reach sooner than opponent; tie-break by closeness.
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer cells where we are closer; otherwise still consider near ones.
            key = (do - ds, -ds, - (abs(rx - x) + abs(ry - y)))
            # If contest line, heavily bias resources on that same row/col.
            if sweep_row and ry == sy:
                key = (key[0] + 1000, key[1], key[2])
            if sweep_col and rx == sx:
                key = (key[0] + 1000, key[1], key[2])
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    best_move = [0, 0]
    best_score = -10**18

    # Deterministic tie-break: fixed order dirs already.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        target = best_resource_from(nx, ny)
        if target is None:
            continue
        rx, ry = target

        ds_next = cheb(nx, ny, rx, ry)
        do_now = cheb(ox, oy, rx, ry)
        self_adv = do_now - ds_next  # higher is better

        # Also account for near-term pickup chance.
        pickup_bonus = 120 if cheb(nx, ny, rx, ry) == 0 else 0
        # If we are on contest line, push along it toward center of remaining resources deterministically.
        line_push = 0
        if sweep_row and ry == sy:
            line_push = 10 * (1 if nx > sx else (-1 if nx < sx else 0))
        if sweep_col and rx == sx:
            line_push = 10 * (1 if ny > sy else (-1 if ny < sy else 0))

        score = self_adv * 100 + pickup_bonus + line_push - 0.5 * ds_next

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move