def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def valid_moves():
        out = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((dx, dy))
        return out

    vm = valid_moves()
    if not vm:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # No resources: move to a deterministic intercept point near the opponent.
    if not resources:
        tx = (sx + ox) // 2
        ty = (sy + oy) // 2
        best = None
        bestk = None
        for dx, dy in vm:
            nx, ny = sx + dx, sy + dy
            k = (man(nx, ny, tx, ty), man(nx, ny, ox, oy), dx, dy)
            if bestk is None or k < bestk:
                bestk, best = k, (dx, dy)
        return [best[0], best[1]]

    # Opponent target: closest remaining resource.
    opp_target = min(resources, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))

    # Evaluate each move by best contestable resource (prefer resources where we are closer than opponent).
    best_move = None
    best_score = None
    best_t = None

    for dx, dy in vm:
        nx, ny = sx + dx, sy + dy
        best_r_score = None
        best_r_t = None
        for r in resources:
            rx, ry = r
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Advantage: higher when we are closer than opponent; strongly punish being behind.
            adv = od - sd
            contest_bonus = 60 if r == opp_target else 0
            # Prefer immediate progress, and avoid getting too far.
            s = adv * 12 - sd + contest_bonus
            # If tied, prefer nearer resources for next step deterministically.
            t = (sd, -adv, rx, ry)
            if best_r_score is None or (s, -t[0], t[1], t[2], t[3]) > (best_r_score, -best_r_t[0], best_r_t[1], best_r_t[2], best_r_t[3]):
                best_r_score, best_r_t = s, t
        # Tie-break on moving towards opponent slightly to support shadow/archetype pressure.
        opp_dist = man(nx, ny, ox, oy)
        key = (best_r_score, -best_r_t[0], -best_r_t[1], -opp_dist, dx, dy)
        if best_score is None or key > best_score:
            best_score, best_move = key, (dx, dy)

    return [best_move[0], best_move[1]]