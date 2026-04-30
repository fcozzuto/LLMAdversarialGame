def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def nearest(from_pos, prefer=None):
        best = None
        best_d = None
        for r in resources:
            if prefer is not None and r != prefer:
                continue
            d = dist2(from_pos, r)
            if best is None or d < best_d or (d == best_d and (r[0], r[1]) < (best[0], best[1])):
                best = r
                best_d = d
        if prefer is not None and best is not None:
            return best
        # full search
        best = None
        best_d = None
        for r in resources:
            d = dist2(from_pos, r)
            if best is None or d < best_d or (d == best_d and (r[0], r[1]) < (best[0], best[1])):
                best = r
                best_d = d
        return best

    t_self = nearest((sx, sy))
    t_opp = nearest((ox, oy))
    if t_self == t_opp:
        t_alt = None
        best_d = None
        for r in resources:
            if r == t_self:
                continue
            d = dist2((sx, sy), r)
            if best_d is None or d < best_d or (d == best_d and (r[0], r[1]) < (t_alt[0], t_alt[1])):
                t_alt = r
                best_d = d
        target = t_alt if t_alt is not None else t_self
    else:
        target = t_self

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_target = dist2((nx, ny), target)
        d_opp = dist2((nx, ny), (ox, oy))
        # minimize distance to target; maximize distance from opponent
        key = (d_target, -d_opp, abs(dx), abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]