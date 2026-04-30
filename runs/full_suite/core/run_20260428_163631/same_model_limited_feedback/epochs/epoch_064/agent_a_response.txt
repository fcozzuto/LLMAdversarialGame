def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Choose a target resource that we can reach sooner than opponent (with bias to staying ahead)
    best = None
    best_key = None
    for r in resources:
        dS = dist((sx, sy), tuple(r))
        dO = dist((ox, oy), tuple(r))
        key = (dS - 0.85 * dO, dS, abs(r[0] - sx) + abs(r[1] - sy), r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = (r[0], r[1])
    if best is None:
        # No resources visible; move to reduce distance to opponent's position (avoid deadlock)
        tx, ty = ox, oy
    else:
        tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that approach target; avoid stepping into obstacles/outside grid.
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cur_d = dist((sx, sy), (tx, ty))
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dist((nx, ny), (tx, ty))
        # Secondary objective: avoid giving opponent an immediate win by not moving into a position
        # where opponent becomes strictly closer to our target than we are.
        my_gap = nd - 0.85 * dist((ox, oy), (tx, ty))
        opp_adv = dist((ox, oy), (tx, ty)) - dist((nx, ny), (tx, ty))
        score = (nd, my_gap, -opp_adv, dx, dy, (nx - tx) ** 2 + (ny - ty) ** 2)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If all candidate moves were invalid (rare), stay.
    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]