def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set((p[0], p[1]) for p in obstacles)

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    nearest = min(resources, key=lambda r: manh(my, r))
    tx, ty = nearest[0], nearest[1]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    res_set = set((r[0], r[1]) for r in resources)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        if (nx, ny) == (ox, oy):
            continue

        if (nx, ny) in res_set:
            score = 10**6
        else:
            after = (nx, ny)
            d_after = min(manh(after, r) for r in resources)
            d_now = manh(my, nearest)
            improve = d_now - d_after

            toward = -(abs(nx - tx) + abs(ny - ty))
            opp_dist = abs(nx - ox) + abs(ny - oy)
            score = 2000 * improve + 3 * toward + 0.5 * opp_dist

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]