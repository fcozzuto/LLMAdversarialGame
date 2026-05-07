def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        return [0, 0]

    res_list = [tuple(r) for r in resources]
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        lead_count = 0
        best_adv = -10**9
        best_dist = 10**9
        for rx, ry in res_list:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv:
                best_adv = adv
                best_dist = ds
            if adv > 0:
                lead_count += 1
            elif adv == 0:
                lead_count += 0  # tie doesn't increase
        # Prefer moves that create a strong lead; secondarily get closer and increase number of winnable resources.
        # Add a mild urgency to not stall when leading is possible.
        stall_pen = -0.75 if dx == 0 and dy == 0 and any((cheb(nx, ny, rx, ry) < cheb(ox, oy, rx, ry)) for rx, ry in res_list) else 0.0
        urgency = 0.01 * (turns_remaining if turns_remaining is not None else 0)
        val = (best_adv * 10.0) + (-best_dist * 0.25) + (lead_count * 1.6) + stall_pen + urgency
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]