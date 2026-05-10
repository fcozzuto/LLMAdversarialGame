def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def opp_next_toward(tx, ty):
        dx = 0 if ox == tx else (1 if tx > ox else -1)
        dy = 0 if oy == ty else (1 if ty > oy else -1)
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            return nx, ny
        # fallback: best among legal one-step moves toward target
        best = (ox, oy, man(ox, oy, tx, ty))
        for mdx, mdy in moves:
            ax, ay = ox + mdx, oy + mdy
            if inb(ax, ay) and (ax, ay) not in obst:
                d = man(ax, ay, tx, ty)
                if d < best[2]:
                    best = (ax, ay, d)
        return best[0], best[1]

    best_move = (0, 0)
    best_key = (-10**18, 10**18)

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # maximize our advantage after a likely opponent step toward the same resource
        my_best = -10**18
        my_tie = 10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            ox2, oy2 = opp_next_toward(rx, ry)
            od = man(ox2, oy2, rx, ry)
            adv = od - sd  # >0 means we are likely earlier
            if adv > my_best or (adv == my_best and sd < my_tie):
                my_best = adv
                my_tie = sd
        key = (my_best, my_tie)
        if key > best_key:
            best_key = key
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]