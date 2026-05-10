def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_pick = None  # (resource_index, mydist, oddist)
    for i, (rx, ry) in enumerate(resources):
        if (rx, ry) == (sx, sy):
            return [0, 0]
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if best_pick is None:
            best_pick = (i, sd, od)
        else:
            # Prefer resources where opponent is closer (we want to intercept/deny).
            # If none, pick nearest to us.
            if (od < best_pick[2]) or (best_pick[1] > 7 and sd < best_pick[1]):
                best_pick = (i, sd, od)

    i, sd, od = best_pick
    rx, ry = resources[i]

    # Intercept point: step from opponent towards the resource (simple one-move lookahead),
    # then bias towards positions near that point while not stepping into obstacles.
    tx, ty = ox, oy
    if ox < rx:
        tx += 1
    elif ox > rx:
        tx -= 1
    if oy < ry:
        ty += 1
    elif oy > ry:
        ty -= 1
    if not in_bounds(tx, ty):
        tx, ty = ox, oy  # fallback

    best_move = [0, 0]
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        # Primary: deny capture by minimizing distance to intercept point,
        # while also making it harder for opponent to get to the chosen resource next.
        my_to_t = man(nx, ny, tx, ty)
        opp_to_next_res = man(tx, ty, rx, ry)

        my_to_res = man(nx, ny, rx, ry)
        opp_to_res = man(ox, oy, rx, ry)

        # If we are already leading, shift to direct pickup.
        lead = 1 if my_to_res <= opp_to_res else 0

        # Obstacle proximity penalty (discourage near-wall/blocked traps).
        wall_pen = 0
        for ax, ay in ((nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1), (nx+1, ny+1), (nx-1, ny-1)):
            if not in_bounds(ax, ay):
                wall_pen += 1

        score = 1000 * (0 if lead else (-my_to_t)) + (50 if lead else 0) * (-(my_to_res)) + (30 * (opp_to_next_res)) - 3 * wall_pen
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move