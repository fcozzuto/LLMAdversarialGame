def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a materially different strategic target: contest resources by relative reach.
    best = None
    any_we_closer = False
    for r in resources:
        r = (r[0], r[1])
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        diff = do - ds  # positive => we can reach sooner
        if diff > 0:
            any_we_closer = True
        cand = diff if any_we_closer else -do  # if we can't win any, deny opponent's nearest
        if best is None:
            best = (r, cand)
        else:
            if any_we_closer:
                if diff > best[1]:
                    best = (r, diff)
            else:
                if -do > best[1]:
                    best = (r, -do)

    tx, ty = best[0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        # Primary: get closer to target; Secondary: keep distance from opponent to reduce capture races.
        key = (d_to_t, -d_opp)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]