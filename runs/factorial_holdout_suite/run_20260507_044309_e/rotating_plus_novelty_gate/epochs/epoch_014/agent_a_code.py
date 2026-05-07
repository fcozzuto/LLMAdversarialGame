def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    def man(ax, ay, bx, by):
        a = ax - bx
        if a < 0: a = -a
        b = ay - by
        if b < 0: b = -b
        return a + b

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18
    # Deterministic: break ties by move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        best_adv = -10**9
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - our_d  # positive => closer than opponent
            if adv > best_adv:
                best_adv = adv
        # Prefer being closer than opponent; otherwise still move toward resources.
        val = best_adv * 100 - man(nx, ny, sx, sy)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move