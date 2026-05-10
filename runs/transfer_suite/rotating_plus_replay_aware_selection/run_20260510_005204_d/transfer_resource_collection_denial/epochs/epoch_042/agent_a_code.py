def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = {tuple(p) for p in obs_list}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: cheb(sx, sy, p[0], p[1]) - 0.001 * (p[0] + p[1]))  # deterministic
        best = [0, 0]
        bestv = -10**9
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = -cheb(nx, ny, tx, ty)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Pick a target resource that we can reach earlier than the opponent, with tie-breaks.
    best_r = resources[0]
    best_key = None
    my_to_center = -(abs(sx - (w - 1) / 2.0) + abs(sy - (h - 1) / 2.0))
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        center_bonus = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        key = ((opd - myd), -(myd), center_bonus, -(rx + 2 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # Greedy one-step selection maximizing advantage; add small preference to not drift away.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    cur_myd = cheb(sx, sy, tx, ty)
    cur_opd = cheb(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)

        # Prefer immediate collection: if moving onto a resource, value it most.
        on_resource = 1 if [nx, ny] in resources or (nx, ny) in {tuple(p) for p in resources} else 0
        center = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        progress = (cur_myd - myd2)  # positive if we get closer

        adv = (opd2 - myd2) - (cur_opd - cur_myd)  # improve our lead
        val = (1000000 * on_resource) + (1000 * (opd2 - myd2)) + (50 * progress) + (0.1 * center) - 0.01 * (abs(dx) + abs(dy))
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move