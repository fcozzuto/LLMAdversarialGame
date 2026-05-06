def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obstacles_raw)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    best = -10**18

    # Interceptor-style: prioritize resources on/near opponent's current row (sweep_rows archetype).
    opp_row_pen = 1e9
    for rx, ry in resources:
        d = abs(ry - oy)
        if d < opp_row_pen:
            opp_row_pen = d
    row_target_scale = 4 if opp_row_pen <= 1 else 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_best, opp_best = 10**9, 10**9
        my_row, opp_row = 10**9, 10**9
        for rx, ry in resources:
            md = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if md < my_best:
                my_best = md
            if od < opp_best:
                opp_best = od
            my_row = min(my_row, abs(ry - ny))
            opp_row = min(opp_row, abs(ry - oy))

        # Core: win nearest-resource contest, with stronger push when ahead.
        score = (opp_best - my_best) * 6 - my_best

        # Interception: keep my y aligned with resources near opponent's sweep row.
        score += (row_target_scale * (opp_row - my_row))

        # Switch pressure: if opponent is extremely close to some resource, reduce my distance even if farther by general heuristic.
        if opp_best <= 2:
            score += (5 - my_best) * 3

        # Slight preference for progressing toward the closest resource (reduces dithering).
        cur_my = 10**9
        for rx, ry in resources:
            cur_my = min(cur_my, man(sx, sy, rx, ry))
        score += (cur_my - my_best)

        if score > best or (score == best and (dx, dy) < (best_dx, best_dy)):
            best = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]