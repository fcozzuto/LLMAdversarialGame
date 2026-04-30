def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]
    best = None
    best_val = -10**18

    opp_nearest_r = None
    opp_nearest_d = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < opp_nearest_d:
            opp_nearest_d = d
            opp_nearest_r = (rx, ry)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Race resources where we have advantage; if we have none, try to get closer to opponent's likely target.
        val = 0.0
        any_pos = False
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > 0:
                any_pos = True
                val += 3.5 * adv
                if ds == 0:
                    val += 1000.0
                elif ds == 1:
                    val += 7.0
            else:
                # small penalty for being closer than opponent (might be "donated" by them)
                if ds <= do:
                    val -= 1.0

        if not any_pos and opp_nearest_r is not None:
            rx, ry = opp_nearest_r
            d_now = cheb(nx, ny, rx, ry)
            val += 25.0 * (-d_now)
            # slight pressure towards the opponent to potentially deny paths
            d_opp_next = cheb(nx, ny, ox, oy)
            val += -0.35 * d_opp_next

        # Gentle preference for staying away from obstacles' vicinity by penalizing moves adjacent to obstacles
        adj_pen = 0
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) == 1:
                adj_pen += 1
        val -= 2.0 * adj_pen

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best