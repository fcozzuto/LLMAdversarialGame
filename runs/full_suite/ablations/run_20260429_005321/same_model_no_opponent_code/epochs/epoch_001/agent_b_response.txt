def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x0, y0 = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    res_set = set((p[0], p[1]) for p in resources)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_sq(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    opp_dist_cache = {}
    for rx, ry in resources:
        opp_dist_cache[(rx, ry)] = dist_sq(ox, oy, rx, ry)

    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = x0 + dx, y0 + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        on_res = 1 if (nx, ny) in res_set else 0
        if resources:
            # Primary: capture/advantage, Secondary: minimize my distance
            my_best_dist = None
            my_best_adv = None
            for rx, ry in resources:
                myd = dist_sq(nx, ny, rx, ry)
                my_best_dist = myd if my_best_dist is None else min(my_best_dist, myd)
                adv = opp_dist_cache[(rx, ry)] - myd
                if my_best_adv is None or adv > my_best_adv:
                    my_best_adv = adv
            key = (on_res, my_best_adv, -my_best_dist)
        else:
            key = (on_res, 0, 0)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]