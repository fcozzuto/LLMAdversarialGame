def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        # If no visible resources, head to the corner farther from opponent (reduces denial chances)
        target = (0, 0) if (sx + sy) > (ox + oy) else (w - 1, h - 1)
        tx, ty = target
        best = (0, 0)
        bestv = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = abs(nx - tx) + abs(ny - ty) - 0.2 * (abs(nx - ox) + abs(ny - oy))
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Choose a "most promising" resource for this step, then score the step itself
        self_to_best = 10**9
        opp_to_best = 10**9
        res_score = -10**9
        for r in resources:
            rx, ry = r[0], r[1]
            self_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            rr = r[2] if len(r) > 2 else 1
            # Prefer resources we can reach sooner; also value immediate point gain
            cand = (opp_d - self_d) + 0.01 * rr
            if self_d < self_to_best or (self_d == self_to_best and cand > res_score):
                self_to_best = self_d
                opp_to_best = opp_d
                res_score = cand

        # Core: minimize our distance while penalizing moving into resource that opponent can reach first
        # If opponent can reach <= our distance by margin, deny is likely; add strong penalty.
        deny_pen = 0
        if opp_to_best <= self_to_best:
            deny_pen = 5 * (self_to_best - opp_to_best + 1)
        # Also slightly discourage giving opponent closer access by moving towards their position overall
        v = (self_to_best - 0.02 * res_score) + deny_pen + 0.03 * (abs(nx - ox) + abs(ny - oy))

        if v < bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]