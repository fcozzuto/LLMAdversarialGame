def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = observation.get("obstacles") or []
    res = observation.get("resources") or []

    obs_set = set()
    for p in obs:
        obs_set.add((p[0], p[1]))

    if not res:
        # No resources: move to reduce distance to opponent.
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
        best = (0, 0)
        best_val = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
                nx, ny = sx, sy
            val = -max(abs(nx - ox), abs(ny - oy))
            if val > best_val:
                best_val = val
                best = (dx if 0 <= sx + dx < w and (sx + dx, sy) not in obs_set else 0,
                        dy if 0 <= sy + dy < h and (sx, sy + dy) not in obs_set else 0)
        return [best[0], best[1]]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    res_list = [(p[0], p[1]) for p in res]
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
            nx, ny = sx, sy

        # Score: if we can reach a resource sooner than opponent, prefer it.
        cur = -10**18
        for rx, ry in res_list:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > cur:
                cur = adv
        # Small tie-break: prefer staying closer to opponent.
        cur = cur * 1000 - cheb(nx, ny, ox, oy)
        if cur > best_score:
            best_score = cur
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]