def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        best, bestv = (0, 0), None
        for dx, dy in sorted(legal):
            nx, ny = sx + dx, sy + dy
            v = man(nx, ny, cx, cy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Preselect best resource to contest: maximize "how much closer we can become than opponent"
    best_target = None
    best_tscore = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # If opponent is already very close, still allow but prefer those where we can reduce gap fast.
        tscore = (od - sd)
        if best_tscore is None or tscore > best_tscore or (tscore == best_tscore and (rx + ry) < (best_target[0] + best_target[1])):
            best_tscore = tscore
            best_target = (rx, ry)
    trx, tryy = best_target

    # Move evaluation: primary goal go to target; secondary deny closer enemy resources
    # Deny term encourages reducing opponent-accessible distances when we are disadvantaged.
    def closest_dist(posx, posy):
        bestd = None
        for rx, ry in resources:
            d = man(posx, posy, rx, ry)
            if bestd is None or d < bestd:
                bestd = d
        return bestd if bestd is not None else 0

    best_move, best_val = (0, 0), None
    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy
        # primary: advance toward target
        self_t = man(nx, ny, trx, tryy)
        # deny: for each resource where opponent is ahead, reduce that opponent's advantage
        deny = 0
        for rx, ry in resources:
            od = man(ox, oy, rx, ry)
            sd_now = man(sx, sy, rx, ry)
            if od + 0.0 < sd_now:  # opponent closer than us now
                self_future = man(nx, ny, rx, ry)
                # if we can get close, reduce their edge
                denom = 1 + self_future
                deny += (od - self_future) / denom
        # encourage keeping options: slightly prefer moves that increase our nearest-resource progress
        self_closest = closest_dist(nx, ny)
        # center bias to avoid getting stuck near corners
        center_bias = -0.02 * man(nx, ny, cx, cy)

        val = (-2.2 * self_t) + (1.0 * deny) + (-0.08 * self_closest) + center_bias
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]