def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    occ = set((x, y) for x, y in obstacles)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    if not resources:
        return [0, 0]

    # Choose the resource that best favors us over the opponent.
    best_r = None
    best_score = None
    for r in resources:
        d1 = dist((sx, sy), tuple(r))
        d2 = dist((ox, oy), tuple(r))
        sc = (d1 - 0.6 * d2, d1, d2, r[0], r[1])
        if best_score is None or sc < best_score:
            best_score = sc
            best_r = tuple(r)

    tx, ty = best_r
    # Move greedily toward target, with obstacle avoidance.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    chosen = (0, 0)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in occ:
            continue
        nd = dist((nx, ny), (tx, ty))
        # Prefer reducing distance; slight bias to avoid stepping near opponent.
        opp_d = dist((nx, ny), (ox, oy))
        sc = (nd, -opp_d, dx, dy)
        if best is None or sc < best:
            best = sc
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]