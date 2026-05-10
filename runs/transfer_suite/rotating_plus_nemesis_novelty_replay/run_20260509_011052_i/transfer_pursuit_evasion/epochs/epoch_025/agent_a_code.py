def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def kingd(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_away(x, y):
        return max(corners, key=lambda c: abs(x - c[0]) + abs(y - c[1]))
    def corner_toward(x, y):
        return min(corners, key=lambda c: abs(x - c[0]) + abs(y - c[1]))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_evader = "evader" in self_role
    opp_is_evader = "evader" in opp_role

    def best_step_for_agent(ax, ay, bx, by, evade):
        # evade=True: maximize distance + drift to far corner; else: minimize distance + drift to toward corner
        corner = corner_away(bx, by) if evade else corner_toward(bx, by)
        best = (ax, ay)
        bestv = -10**18 if evade else 10**18
        for dx, dy in dirs:
            nx, ny = ax + dx, ay + dy
            if not inside(nx, ny):
                continue
            d = kingd(nx, ny, bx, by)
            dc = abs(nx - corner[0]) + abs(ny - corner[1])
            v = (d + 0.06 * dc) if evade else (-d + 0.01 * dc)
            if evade:
                if v > bestv:
                    bestv = v
                    best = (nx, ny)
            else:
                if v < bestv:
                    bestv = v
                    best = (nx, ny)
        return best

    # predict opponent next move
    if opp_is_evader:
        pred_ox, pred_oy = best_step_for_agent(ox, oy, sx, sy, True)
    else:
        pred_ox, pred_oy = best_step_for_agent(ox, oy, sx, sy, False)

    best_move = (0, 0)
    if i_am_evader:
        # move away from predicted opponent
        targetx, targety = pred_ox, pred_oy
        corner = corner_away(sx, sy)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = kingd(nx, ny, targetx, targety)
            dc = abs(nx - corner[0]) + abs(ny - corner[1])
            v = d + 0.08 * dc
            if v > bestv:
                bestv = v
                best_move = (dx, dy)
    else:
        # pursue predicted opponent (greedy)
        targetx, targety = pred_ox, pred_oy
        bestv = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = kingd(nx, ny, targetx, targety)
            # small tie-break to avoid oscillation toward center-ish
            tie = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
            v = d + 0.001 * tie
            if v < bestv:
                bestv = v
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]