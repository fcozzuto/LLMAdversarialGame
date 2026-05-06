def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    # If no resources, move to reduce distance to opponent's likely area (center-ish).
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = (0, 0)
    best_val = -10**18

    # Deterministic tie-break: prefer lower (dx,dy) lexicographically among equals.
    def lex_key(d):
        return (d[0], d[1])

    opp_now = king(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Advantage for us: opponent_dist - our_dist for each resource.
        # We want the best achievable advantage; penalize moves that give opponent safe access.
        best_adv = -10**9
        worst_lose = 10**9
        near_ours = 10**9
        near_opp = 10**9

        for rx, ry in resources:
            ds = king(nx, ny, rx, ry)
            do = king(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            if adv > best_adv:
                best_adv = adv
            # If opponent is much closer than us, track worst loss
            lose = ds - do  # negative is losing; larger means better
            if lose < worst_lose:
                worst_lose = lose
            dso = king(nx, ny, rx, ry)
            if dso < near_ours:
                near_ours = dso
            dop = king(ox, oy, rx, ry)
            if dop < near_opp:
                near_opp = dop

        # Score: primary best_adv, secondary: avoid being the one far behind,
        # tertiary: move to reduce our distance to the closest resource.
        # Also slightly prefer moves that don't make opponent approach us faster.
        val = 0
        val += 1000 * best_adv
        val += -200 * max(0, -worst_lose)  # penalize if we're behind on all good options
        val += -5 * near_ours
        val += -1 * max(0, opp_now - king(nx, ny, ox, oy))  # discourage improving opponent proximity to us

        cand = (dx, dy)
        if val > best_val or (val == best_val and lex_key(cand) < lex_key(best)):
            best_val = val
            best = cand

    return [int(best[0]), int(best[1])]