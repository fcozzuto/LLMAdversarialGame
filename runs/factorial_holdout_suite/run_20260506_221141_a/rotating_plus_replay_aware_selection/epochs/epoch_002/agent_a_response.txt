def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = observation["obstacles"]
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation["resources"]

    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            md = abs(rx - x) + abs(ry - y)
            od = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can reach earlier; then closer; then top-left tie-break
            key = ((md - od), md, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        if best is not None:
            tx, ty = best[1]
            best_step = None
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not in_bounds(nx, ny) or (nx, ny) in obs:
                    continue
                d_t = abs(tx - nx) + abs(ty - ny)
                # If opponent also close, bias to reduce their advantage
                d_o = abs(tx - ox) + abs(ty - oy)
                my_adv = (d_t - d_o)
                # Deterministic tie-break favoring not moving away and lexicographic step
                step_key = (d_t, my_adv, dx, dy)
                if best_step is None or step_key < best_step[0]:
                    best_step = (step_key, (dx, dy))
            if best_step is not None:
                return [int(best_step[1][0]), int(best_step[1][1])]

    # No viable target: move to safest low-obstacle neighborhood while slightly increasing distance from opponent
    best_step = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        # count adjacent obstacles (including resource squares as neutral)
        adj_obs = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            ax, ay = nx + adx, ny + ady
            if in_bounds(ax, ay) and (ax, ay) in obs:
                adj_obs += 1
        dist_o = abs(ox - nx) + abs(oy - ny)
        key = (adj_obs, -dist_o, dx, dy)
        if best_step is None or key < best_step[0]:
            best_step = (key, (dx, dy))
    if best_step is None:
        return [0, 0]
    return [int(best_step[1][0]), int(best_step[1][1])]