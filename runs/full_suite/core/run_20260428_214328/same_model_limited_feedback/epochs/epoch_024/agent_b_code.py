def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    if [sx, sy] in resources:
        return [0, 0]
    # Choose a resource where we are relatively closer than the opponent
    def ds2(a, b):  # squared euclidean
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy
    best_r = None
    best_key = None
    for r in resources:
        self_d = ds2((sx, sy), r)
        opp_d = ds2((ox, oy), r)
        # Prefer resources where we are closer (larger advantage => smaller (self-opp))
        key = (self_d - opp_d, self_d, -(r[0] * 17 + r[1] * 31))
        if best_key is None or key < best_key:
            best_key = key
            best_r = r
    tx, ty = best_r if best_r is not None else (sx, sy)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        target_d = ds2((nx, ny), (tx, ty))
        opp_d = ds2((nx, ny), (ox, oy))
        # Primary: minimize distance to target. Secondary: keep distance from opponent.
        # Tertiary: deterministic tie-break.
        key = (target_d, -opp_d, dx * 3 + dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]