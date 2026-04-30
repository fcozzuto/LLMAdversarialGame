def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obs_set = set((x, y) for x, y in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_pos(x, y):
        # If landing on obstacle, heavily penalize (engine may keep us in place anyway).
        if (x, y) in obs_set:
            return -10**9

        if resources:
            best_d = 10**9
            for rx, ry in resources:
                dx = rx - x
                dy = ry - y
                d = dx*dx + dy*dy  # squared euclidean
                if d < best_d:
                    best_d = d
            # Prefer closer to resources; also slightly prefer moving in a way that doesn't open paths for opponent.
            d_opp = (ox - x)*(ox - x) + (oy - y)*(oy - y)
            return -best_d - 0.06 * d_opp
        else:
            # No resources: chase opponent to deny.
            d_opp = (ox - x)*(ox - x) + (oy - y)*(oy - y)
            return -d_opp

    best = None
    best_sc = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        sc = score_pos(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best