def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def md(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            k = (md(nx, ny, cx, cy), md(nx, ny, ox, oy), dx, dy)
            if best is None or k < best:
                best, best_move = k, [dx, dy]
        return best_move

    best_key = None
    best_move = [0, 0]

    # Choose move that maximizes potential to be closer to some resource than the opponent.
    # Score: prefer smaller my distance, larger distance advantage; add mild safety vs opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        my_best = 10**9
        opp_best = 10**9
        advantage_best = -10**9
        tie_break = 10**9

        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            if myd < my_best:
                my_best = myd
            if opd < opp_best:
                opp_best = opd
            adv = opd - myd  # positive means we are closer than opponent to that resource
            if adv > advantage_best:
                advantage_best = adv
                tie_break = myd

        # Safety: discourage approaching opponent when not winning any resource contest.
        my_to_opp = md(nx, ny, ox, oy)
        safety_penalty = 0 if my_to_opp >= 3 else (3 - my_to_opp) * 0.2

        # Lexicographic key: maximize advantage, then minimize my distance to best contest,
        # then maximize distance from opponent, then deterministic move preference.
        key = (
            -(advantage_best * 1000 + (1 if tie_break == 0 else 0)),  # bigger adv -> smaller key
            tie_break,
            -(my_to_opp),
            dx, dy
        )

        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move