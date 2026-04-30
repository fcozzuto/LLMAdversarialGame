def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obs_set = set((p[0], p[1]) for p in obstacles)
    res_list = [(r[0], r[1]) for r in resources]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, move to improve relative position (toward opponent away from edge)
    if not res_list:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                nx, ny = sx, sy
            # prefer increasing distance from opponent while moving toward center
            center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            obj = (dist((nx, ny), (ox, oy))) + 0.01 * center_bias
            if best is None or obj > best[0] or (obj == best[0] and dist((nx, ny), (w // 2, h // 2)) < best[1]):
                best = (obj, dist((nx, ny), (w // 2, h // 2)), dx, dy)
        return [best[2], best[3]]

    best_obj = None
    best_dself = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Choose the target that gives the best advantage for this move.
        dself_to_best = 10**9
        best_gap = -10**9
        for rx, ry in res_list:
            d_s = dist((nx, ny), (rx, ry))
            d_o = dist((ox, oy), (rx, ry))
            gap = d_o - d_s  # positive means closer than opponent
            if gap > best_gap or (gap == best_gap and d_s < dself_to_best):
                best_gap = gap
                dself_to_best = d_s

        # Bonus for landing on a resource immediately.
        if (nx, ny) in obs_set:
            continue
        if (nx, ny) in set(res_list):
            best_gap += 1000

        obj = best_gap
        dself = dself_to_best
        if best_obj is None or obj > best_obj or (obj == best_obj and dself < best_dself):
            best_obj = obj
            best_dself = dself
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]