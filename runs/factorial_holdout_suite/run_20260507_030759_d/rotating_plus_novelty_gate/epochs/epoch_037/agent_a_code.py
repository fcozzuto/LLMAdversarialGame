def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    if not resources:
        # Go to farthest corner from opponent while staying legal.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            val = (abs(cx - ox) + abs(cy - oy), -(abs(cx - sx) + abs(cy - sy)))
            if best is None or val > best[0]:
                best = (val, (cx, cy))
        if best is None:
            return [0, 0]
        cx, cy = best[1]
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        if (sx + dx, sy + dy) in obstacles or not inb(sx + dx, sy + dy):
            # fallback: any move that increases distance from opponent
            bx = 0
            by = 0
            bv = -10**9
            for ddx, ddy in moves:
                nx, ny = sx + ddx, sy + ddy
                v = abs(nx - ox) + abs(ny - oy)
                if v > bv:
                    bv = v
                    bx, by = ddx, ddy
            return [bx, by]
        return [dx, dy]

    # Pick a target resource where we are (often) closer than opponent; prioritize tight wins.
    best_target = None
    best_score = None
    for tx, ty in resources:
        myd = abs(tx - sx) + abs(ty - sy)
        opd = abs(tx - ox) + abs(ty - oy)
        # Prefer being strictly closer; strongly prefer much-closer; break ties by my distance and centrality.
        score = (2 * (opd - myd), -myd, -(abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2)))
        if best_score is None or score > best_score:
            best_score = score
            best_target = (tx, ty)

    tx, ty = best_target

    # Among legal moves, choose step that maximizes progress to target, while not letting opponent gain.
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        my_to = abs(tx - nx) + abs(ty - ny)
        opp_to = abs(tx - ox) + abs(ty - oy)
        # Encourage reducing our distance to target; if opponent is close, prioritize increasing their distance to target.
        v = (-(my_to), -(abs(ox - nx) + abs(oy - ny)), (opp_to - my_to), -abs(dx) - abs(dy))
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]