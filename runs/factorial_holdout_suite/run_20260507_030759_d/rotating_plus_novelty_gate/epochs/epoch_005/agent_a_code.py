def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    res_set = set(tuple(p) for p in resources)

    def key_for(pos):
        x, y = pos
        # Opponent's nearest resource (to deny)
        best_opp = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            od = abs(ox - rx) + abs(oy - ry)
            sd = abs(x - rx) + abs(y - ry)
            if best_opp is None or od < best_opp[0] or (od == best_opp[0] and (sd < best_opp[1] or (sd == best_opp[1] and (rx, ry) < best_opp[2]))):
                best_opp = (od, sd, (rx, ry))
        if best_opp is None:
            return -10**9, None

        # Value: deny opponent's nearest; if we can beat them, strongly prefer.
        target = best_opp[2]
        tx, ty = target
        sd = abs(x - tx) + abs(y - ty)
        od = abs(ox - tx) + abs(oy - ty)
        can_take = 1 if (x, y) == target else 0
        # Also allow secondary: any resource where we are closer than opponent.
        best_adv2 = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd2 = abs(x - rx) + abs(y - ry)
            od2 = abs(ox - rx) + abs(oy - ry)
            adv = od2 - sd2
            tup = (adv, -sd2, -rx, -ry)
            if best_adv2 is None or tup > best_adv2[0]:
                best_adv2 = (tup, (rx, ry), sd2, od2)
        adv2, _, _, _ = best_adv2[0]
        if sd == 0:
            return 10**6, target
        # weights: denial first, then immediate advantage, then closeness
        value = 10000 * (1 if od - sd >= 0 else 0) + 5000 * (od - sd) + 200 * can_take + 50 * adv2 - 2 * sd
        return value, target

    # Choose move by evaluating best outcome position (1-step lookahead).
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us; mimic deterministically
        val, tgt = key_for((nx, ny))
        # Tie-break: prefer move that also reduces distance to opponent-target
        if tgt is not None:
            tx, ty = tgt
            dist_to_t = abs(nx - tx) + abs(ny - ty)
        else:
            dist_to_t = 0
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        t = (val, -dist_to_t, dist_to_opp, dx, dy)
        if best_val is None or t > best_val:
            best_val = t
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]