def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    res_list = sorted((r[0], r[1]) for r in resources if r and len(r) >= 2)
    res_set = set(res_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        if (nx, ny) in res_set:
            val = (10**9, -0, 0)
        else:
            # Maximize best advantage over all resources; secondary: minimize our distance to the best target.
            best_adv = -10**9
            best_my = 10**9
            for rx, ry in res_list:
                myd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                adv = opd - myd
                if adv > best_adv or (adv == best_adv and myd < best_my):
                    best_adv = adv
                    best_my = myd
            # Also add a light preference for being closer than the opponent on average via total score.
            tot_diff = 0
            for rx, ry in res_list:
                tot_diff += man(ox, oy, rx, ry) - man(nx, ny, rx, ry)
            val = (best_adv, tot_diff, -best_my)

        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]