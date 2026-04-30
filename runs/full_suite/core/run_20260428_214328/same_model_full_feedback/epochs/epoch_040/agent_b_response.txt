def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cur_opp_best = 10**9
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < cur_opp_best:
            cur_opp_best = d

    best = (-10**18, 0, 0, 0)
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        our_best_adv = -10**18
        our_target_dist = 10**9
        opp_target_dist = 10**9
        for rx, ry in resources:
            d_us = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            adv = d_op - d_us
            if adv > our_best_adv or (adv == our_best_adv and d_us < our_target_dist):
                our_best_adv = adv
                our_target_dist = d_us
                opp_target_dist = d_op

        # If we can't gain on any resource, become more "intercept" oriented:
        # reduce opponent distance to the same closest resource to prevent their runaway.
        # (Use a small weight so positive advantage dominates.)
        if our_best_adv < 0:
            prevent = 0
            for rx, ry in resources:
                if man(ox, oy, rx, ry) == opp_target_dist:
                    prevent = -man(nx, ny, rx, ry)  # approach that resource too
                    break
            prevent = prevent if prevent != 0 else -our_target_dist
        else:
            prevent = 0

        # Tie-breakers: prefer centrality and keeping some distance from opponent
        center_bonus = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
        sep = man(nx, ny, ox, oy)

        score = (our_best_adv * 1000) - our_target_dist + 2 * sep + center_bonus + prevent
        if score > best[0] or (score == best[0] and (nx, ny) < (best[2], best[3])):
            best = (score, dx, nx, ny)
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]