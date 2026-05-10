def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    res = [(r[0], r[1]) for r in resources]

    best_target = None
    best_metric = None
    for rx, ry in res:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        metric = sd - (od // 2)  # favor resources we reach relatively sooner
        if best_metric is None or metric < best_metric or (metric == best_metric and sd < best_target[0]):
            best_metric = metric
            best_target = (sd, rx, ry)

    _, tx, ty = best_target
    opp_bias = abs(ox - tx) + abs(oy - ty)

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in res:
            val = 10**9
        else:
            cur_sd = abs(nx - tx) + abs(ny - ty)
            cur_od = abs(nx - ox) + abs(ny - oy)
            # primary: get closer to our chosen target
            val = -cur_sd
            # secondary: discourage moving into opponent's reach race
            val -= cur_od // 3
            # tertiary: keep away from opponent in sweep-like fashion
            val -= (1 if nx == ox or ny == oy else 0) * 2
            # slight tie-break: reduce distance to some other resources too
            best_other = 10**9
            for rx, ry in res:
                d = abs(nx - rx) + abs(ny - ry)
                if d < best_other:
                    best_other = d
            val -= best_other // 10
            # prefer moves that increase opponent's distance to target
            val -= -((abs(tx - ox) + abs(ty - oy) - opp_bias) // 10)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move