def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    res_list = [tuple(r) for r in resources]
    if not res_list:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        worst = 10**9
        gain = -10**18
        closest = 10**9
        for rx, ry in res_list:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # positive means we can reach strictly earlier than opponent
            adv = do - ds
            if adv > gain:
                gain = adv
            if ds < closest:
                closest = ds
            if adv < worst:
                worst = adv

        # Encourage blocking/denial: if we can't win, reduce opponent's advantage.
        # Slight preference for nearer resources and for not being trapped (move that stays valid).
        val = gain * 1000 + (0 if gain > 0 else (-worst)) * 20 - closest
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]