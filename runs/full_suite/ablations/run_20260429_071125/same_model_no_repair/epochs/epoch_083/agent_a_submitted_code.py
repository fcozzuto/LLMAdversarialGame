def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def best_op_move(tgx, tgy):
        best = (INF, 0, 0)
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tgx, tgy)
            key = (d, dx, dy)
            if key < best:
                best = key
        return (best[1], best[2])

    # Opponent's likely target: the resource closest to them now (ties -> lexicographically smallest)
    best_t = resources[0]
    best_d = cheb(ox, oy, resources[0][0], resources[0][1])
    best_pair = (best_d, best_t[0], best_t[1])
    for rx, ry in resources[1:]:
        d = cheb(ox, oy, rx, ry)
        pair = (d, rx, ry)
        if pair < best_pair:
            best_pair = pair
            best_d = d
            best_t = (rx, ry)

    tgx, tgy = best_t
    odx, ody = best_op_move(tgx, tgy)
    nox, noy = ox + odx, oy + ody
    opp_next_dist = cheb(nox, noy, tgx, tgy)

    # Move that maximizes our advantage on that target; break ties by moving closer to other nearby resources.
    best_mv = (0, 0)
    best_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_ours = cheb(nx, ny, tgx, tgy)
        # If we can reach now, strongly prefer.
        if d_ours == 0:
            val = 10**8 - opp_next_dist
        else:
            val = (opp_next_dist - d_ours) * 1000 - d_ours

        # Tie-break / avoid getting trapped: prefer states that reduce our distance to the closest remaining resource.
        min_other = INF
        for rx, ry in resources:
            dd = cheb(nx, ny, rx, ry)
            if dd < min_other:
                min_other = dd
        val -= min_other

        if val > best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int