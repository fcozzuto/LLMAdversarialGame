def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
            if (nx, ny) in obs:
                continue
            dv = (nx - ox) ** 2 + (ny - oy) ** 2
            if dv > bestv:
                bestv = dv
                best = [dx, dy]
        return best

    best_res = None
    best_val = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        val = ds - 0.75 * do
        if best_val is None or val < best_val:
            best_val = val
            best_res = (rx, ry)
        elif val == best_val:
            if (ds, -do) < (abs(best_res[0] - sx) + abs(best_res[1] - sy), -abs(best_res[0] - ox) - abs(best_res[1] - oy)):
                best_res = (rx, ry)

    tx, ty = best_res
    best = [0, 0]
    best_score = -10**18
    cur_td = (tx - sx) ** 2 + (ty - sy) ** 2
    opp_cur = (ox - sx) ** 2 + (oy - sy) ** 2

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obs:
            continue
        td = (tx - nx) ** 2 + (ty - ny) ** 2
        opp_d = (ox - nx) ** 2 + (oy - ny) ** 2

        # Prefer decreasing distance to target; discourage getting too close to opponent.
        step_gain = cur_td - td
        opp_pen = -0.05 * opp_d if opp_d < opp_cur else 0.02 * (opp_d - opp_cur)  # mild separation bias
        # Small bias to keep moves stable near target.
        align = -0.01 * (abs(tx - nx) + abs(ty - ny))
        score = 10 * step_gain + opp_pen + align

        # Tie-breakers: prefer not moving off-grid (already clamped) and closer to target
        if score > best_score or (score == best_score and (td < (tx - (sx + best[0])) ** 2 + (ty - (sy + best[1])) ** 2)):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]