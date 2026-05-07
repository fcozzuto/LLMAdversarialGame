def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in resources:
            return [dx, dy]

        cur_best = -10**18
        for rx, ry in resources:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            val = d_opp - d_self
            if d_self == 0:
                val += 10**6
            if val > cur_best:
                cur_best = val

        # small tie-break to prefer closer to any resource when values match
        if cur_best == best_val:
            if md(nx, ny, resources[0][0], resources[0][1]) < md(sx + best_move[0], sy + best_move[1], resources[0][0], resources[0][1]):
                best_val = cur_best
                best_move = [dx, dy]
        elif cur_best > best_val:
            best_val = cur_best
            best_move = [dx, dy]

    return best_move