def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Drift toward center deterministically
        cx, cy = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            key = (d, dx, dy)
            if key < best:
                best = key
                bx, by = dx, dy
        return [bx, by] if best[0] != 10**9 else [0, 0]

    best_move = (0, 0)
    best_key = (-10**9, -10**9, 10**9, 10**9)  # maximize adv, then closer, then lower opp_d

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        our_best_adv = -10**9
        our_d_best = 10**9
        opp_d_best = 10**9

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_our
            # Prefer picking before opponent (larger adv), then sooner for us, then later for opponent, then deterministic position
            if adv > our_best_adv or (adv == our_best_adv and (d_our < our_d_best or (d_our == our_d_best and d_opp < opp_d_best))):
                our_best_adv = adv
                our_d_best = d_our
                opp_d_best = d_opp

        # Overall evaluation of the move
        key = (our_best_adv, -our_d_best, opp_d_best, dx + 10 * dy)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]