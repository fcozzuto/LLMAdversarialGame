def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in sorted(legal):
            v = abs((sx + dx) - cx) + abs((sy + dy) - cy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Closest resource now (opponent denial target likelihood)
    mind_opp_res = None
    for rx, ry in resources:
        d = dist(ox, oy, rx, ry)
        if mind_opp_res is None or d < mind_opp_res:
            mind_opp_res = d
            opp_target = (rx, ry)
    trx, tryy = opp_target

    best = None
    best_score = None
    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy

        # Greedy score over resources: gain if we become closer than opponent, else still prefer progress.
        score = 0.0
        best_gain = -10**18
        best_self_next = 10**18
        best_opp_next = 10**18

        for rx, ry in resources:
            self_d_next = dist(nx, ny, rx, ry)
            opp_d_now = dist(ox, oy, rx, ry)
            gain = (opp_d_now - self_d_next)  # positive means we are closer than opponent
            if gain > best_gain:
                best_gain = gain
            if self_d_next < best_self_next:
                best_self_next = self_d_next

            # Approximate opponent next-distance by assuming it also moves 1 step toward that resource
            opp_d_next_est = max(0, opp_d_now - 1)
            if opp_d_next_est < best_opp_next:
                best_opp_next = opp_d_next_est

        # Deny pressure: if opponent's likely target is nearby, move to reduce our distance to it
        deny_d = dist(nx, ny, trx, tryy)

        # Combine: (1) become closer than opponent (2) fastest progress (3) deny its target
        score = 3.0 * best_gain - 0.7 * best_self_next + 0.3 * (best_opp_next) - 0.4 * deny_d

        # Small tie-break: avoid moving away from the board center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = abs(nx - cx) + abs(ny - cy)
        score -= 0.01 * center_pen

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]