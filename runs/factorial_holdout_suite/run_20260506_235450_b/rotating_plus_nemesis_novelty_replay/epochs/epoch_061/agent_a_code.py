def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Target scoring: prefer resources where we can beat opponent (opp_dist - self_dist large),
    # otherwise still go for best net opportunity (self_dist - opp_dist smallest).
    best_target = None
    best_net = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = abs(sx - rx) + abs(sy - ry)
        if opp_exists:
            od = abs(ox - rx) + abs(oy - ry)
            net = (od - sd)  # positive means we are closer
        else:
            net = 0
        if (best_net is None) or (net > best_net) or (net == best_net and sd < abs(sx - (best_target[0] if best_target else rx)) + abs(sy - (best_target[1] if best_target else ry))):
            best_net = net
            best_target = (rx, ry)

    # If no resources, just drift toward center to reduce opponent sweep advantage.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx = 1 if cx > sx else (-1 if cx < sx else 0)
        ty = 1 if cy > sy else (-1 if cy < sy else 0)
        return [tx, ty]

    rx, ry = best_target
    # Evaluate moves: minimize our distance to target, with strong bias to avoid giving opponent a closer claim.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = abs(nx - rx) + abs(ny - ry)
        val = -myd
        if opp_exists:
            opd = abs(ox - rx) + abs(oy - ry)
            myclaim_now = opd - myd
            val += 6 * myclaim_now
            # Additional: don't step into squares that make us worse compared to other nearby resources.
            # (cheap check using one extra contender: nearest resource to opponent)
            best_other = None
            best_other_sd = None
            for r2 in resources:
                r2x, r2y = int(r2[0]), int(r2[1])
                sd2 = abs(nx - r2x) + abs(ny - r2y)
                od2 = abs(ox - r2x) + abs(oy - r2y)
                net2 = od2 - sd2
                if best_other is None or net2 > best_other or (net2 == best_other and sd2 < best_other_sd):
                    best_other, best_other_sd = net2, sd2
            if best_other is not None:
                val += 2 * best_other
        # Slight preference to not move if already on target
        if myd == 0:
            val += 50
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move