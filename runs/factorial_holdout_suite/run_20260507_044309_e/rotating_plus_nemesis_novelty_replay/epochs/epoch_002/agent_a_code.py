def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    nearest_res = min(resources, key=lambda p: md(sx, sy, p[0], p[1]))
    best_move = (0, 0)
    best_val = -10**18
    best_tie = 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in map(tuple, resources):
            return [dx, dy]

        cur_best = -10**18
        for rx, ry in resources:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            val = d_opp - d_self
            if d_self == 0:
                val += 10**6
            # Prefer making progress on resources the opponent is not already closer to
            if md(ox, oy, rx, ry) <= d_self:
                val += 200
            if val > cur_best:
                cur_best = val

        tie = md(nx, ny, nearest_res[0], nearest_res[1])
        # Secondary deterministic tie: reduce distance to opponent to contest likely resources
        tie2 = md(nx, ny, ox, oy)
        if cur_best > best_val or (cur_best == best_val and (tie < best_tie or (tie == best_tie and tie2 < md(sx + best_move[0], sy + best_move[1], ox, oy)))):
            best_val = cur_best
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]