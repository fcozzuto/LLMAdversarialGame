def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not ok(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def nearest_dist(x, y):
        if not resources:
            return 0
        best = 10**9
        for rx, ry in resources:
            d = man(x, y, rx, ry)
            if d < best:
                best = d
        return best

    my_best = -10**18
    best_move = (0, 0)

    my_near_opp = nearest_dist(ox, oy)
    my_near_self = nearest_dist(sx, sy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if resources and (nx, ny) in set(resources):
            val = 1_000_000
        else:
            my_d = nearest_dist(nx, ny)
            opp_d = my_near_opp
            if resources:
                opp_d = nearest_dist(ox, oy)
            gain = opp_d - my_d  # want to be closer than opponent
            # encourage progress and slightly prefer center moves (ties)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = -0.01 * (abs(nx - cx) + abs(ny - cy))
            # if we reduce opponent advantage, reward; if we worsen, punish
            worsen = 0
            if resources:
                cur_diff = nearest_dist(sx, sy) - nearest_dist(ox, oy)
                new_diff = my_d - opp_d
                worsen = -0.5 * (new_diff - cur_diff)
            val = 20 * gain - 0.2 * my_d + center_bias + worsen

        if val > my_best or (val == my_best and (dx, dy) < best_move):
            my_best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]