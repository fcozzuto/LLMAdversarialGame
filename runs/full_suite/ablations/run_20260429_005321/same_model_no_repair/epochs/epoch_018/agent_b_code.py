def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pre-sort resources for deterministic tie-breaking
    res = sorted(resources, key=lambda p: (p[0], p[1]))

    best = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate contested resources: we prefer resources where we're closer than opponent.
        # Also prefer moving to reduce our best contested distance.
        score = 0
        our_best = 10**9
        opp_best_for_our_best = 10**9
        for rx, ry in res:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Weight contested resources strongly: closest to us where we are ahead.
            ahead = d_me - d_opp
            # If we are closer (ahead <=0) reward a lot; if behind, slight penalty.
            if ahead <= 0:
                val = 2000 - 40 * d_me + 5 * (d_opp - d_me)
            else:
                val = -120 - 25 * ahead - 3 * d_me
            score += val

            if d_me < our_best or (d_me == our_best and d_opp < opp_best_for_our_best):
                our_best = d_me
                opp_best_for_our_best = d_opp

        # Additional shaping: keep away from opponent a bit unless we're taking a contested win.
        opp_dist = man(nx, ny, ox, oy)
        winish = 1 if our_best <= opp_best_for_our_best else 0
        score += (3 * opp_dist) if not winish else (6 * (opp_best_for_our_best - our_best + 1))

        # Light penalty for moving away from any resource (prevents dithering)
        cur_min = min(man(sx, sy, rx, ry) for rx, ry in res)
        score -= max(0, our_best - cur_min) * 15

        if score > best_val or (score == best_val and (dx, dy) < tuple(best)):
            best_val = score
            best = [dx, dy]

    return best