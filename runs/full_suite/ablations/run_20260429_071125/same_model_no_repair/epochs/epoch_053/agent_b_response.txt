def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Deterministic: evaluate each move by best "advantage" resource we can race for next.
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        # Prefer moves that increase distance from opponent while closing on a high-value resource.
        best_adv = -10**9
        best_myd = 10**9
        best_r = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer than opponent to that resource
            # Slight bias for resources nearer to us and not behind obstacles-adjacent cells.
            adj_pen = 0
            for ax, ay in ((rx-1, ry), (rx+1, ry), (rx, ry-1), (rx, ry+1)):
                if (ax, ay) in obstacles:
                    adj_pen += 0.05
            val = adv - adj_pen
            if val > best_adv or (val == best_adv and myd < best_myd):
                best_adv, best_myd, best_r = val, myd, (rx, ry)

        # Multi-term deterministic scoring:
        # 1) maximize advantage
        # 2) minimize our distance to the chosen resource
        # 3) maximize separation from opponent (avoid getting too close unless beneficial)
        opp_sep = cheb(nx, ny, ox, oy)
        myd_to_best = best_myd if best_r is not None else cheb(nx, ny, sx, sy)
        score = (best_adv, -myd_to_best, opp_sep)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]