def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Choose a target that we can "reach sooner" most deterministically.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = man(sx, sy, rx, ry)
        op_d = man(ox, oy, rx, ry)
        # Primary: maximize (op_d - my_d), secondary: shorter my_d, then closer to our corner-ish.
        key = (op_d - my_d, -my_d, -(rx + ry))
        if best_key is None or key > best_key:
            best_key, best_t = key, (rx, ry)

    tx, ty = best_t

    # Move greedily, but evaluate each neighbor by advantage after the move and safety from opponent.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = man(nx, ny, tx, ty)
        op_d = man(ox, oy, tx, ty)
        adv = op_d - my_d  # higher is better
        # Safety: discourage getting too close if advantage isn't strong yet
        my_to_opp = man(nx, ny, ox, oy)
        opp_to_me = man(ox, oy, nx, ny)
        safety = my_to_opp - opp_to_me  # deterministic, usually 0, but keeps tie-breaking stable

        # If not winning the target, prefer reducing my distance and moving toward same row/col to counter sweeps.
        row_progress = -abs(ny - ty)  # closer in y to target is good for sweep-row opponents
        col_progress = -abs(nx - tx)
        val = (adv * 1000) + (-my_d * 10) + (row_progress + col_progress) + safety

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move