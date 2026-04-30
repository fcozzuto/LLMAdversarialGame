def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b):
        dx = a[0] - b[0]; dx = dx if dx >= 0 else -dx
        dy = a[1] - b[1]; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Pick a target deterministically by arrival advantage.
    best = None
    best_key = None
    sd = (sx, sy); od = (ox, oy)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        s_time = cheb(sd, (rx, ry))
        o_time = cheb(od, (rx, ry))
        adv = o_time - s_time  # higher => we can arrive no later than opponent
        # Deterministic tie-breakers favor faster, then stable hash.
        key = (adv, -s_time, -((rx * 29 + ry * 31) % 1000003))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    opp_time = cheb((ox, oy), (tx, ty))
    # Secondary objective: also keep pressure on another resource to avoid tunnel vision.
    other_best_dist = 10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles or (rx, ry) == (tx, ty):
            continue
        d = cheb(sd, (rx, ry))
        if d < other_best_dist:
            other_best_dist = d

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        new_sd = (nx, ny)
        new_s_time = cheb(new_sd, (tx, ty))
        # Primary: maximize remaining advantage to reach target.
        score = opp_time - new_s_time
        # Encourage improving distance to target.
        cur_d = cheb(sd, (tx, ty))
        new_d = cheb(new_sd, (tx, ty))
        score = score * 100 + (cur_d - new_d)
        # If target is too far, improve at least one other option deterministically.
        if other_best_dist < 10**8:
            # compute nearest other distance after move (cheap: only among up to 6 closest resources)
            ds = []
            for rx, ry in resources:
                if (rx, ry) in obstacles or (rx, ry) == (tx, ty):
                    continue
                ds.append((cheb(new_sd, (rx, ry)), rx, ry))
            if ds:
                ds.sort(key=lambda t: (t[0], -((t[1]*29+t[2]*31)%1000003)))
                score += 5 * (-ds[0][0])

        # Deterministic tie-break: prefer lexicographically smaller move if score equal.
        tie_key = (-score, dx, dy)
        if best_score is None or score > best_score or (score == best_score and tie_key < (-best_score, best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]