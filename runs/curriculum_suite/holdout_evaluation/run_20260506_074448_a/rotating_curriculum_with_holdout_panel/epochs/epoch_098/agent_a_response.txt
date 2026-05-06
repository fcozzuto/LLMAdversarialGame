def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_my = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            d_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            sc = -(d_my) - 1.0 * d_op
            if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Advantage on resources: prefer states where we are closer than opponent.
        best_adv = -10**18
        best_tiebreak = 10**18
        for rx, ry in resources:
            d_my = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
            d_op = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
            adv = d_op - d_my  # larger means we are relatively closer
            if adv > best_adv:
                best_adv = adv
                best_tiebreak = d_my
            elif adv == best_adv and d_my < best_tiebreak:
                best_tiebreak = d_my

        # Also avoid handing a very near resource to opponent:
        # If opponent is extremely close to some resource, prefer moves that increase their distance.
        worst_opp_close = 10**18
        for rx, ry in resources:
            d_op = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
            if d_op < worst_opp_close:
                worst_opp_close = d_op
        # Key: maximize advantage, minimize my distance to chosen resource, maximize separation from opponent.
        sep = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        key = (-(best_adv), best_tiebreak, -sep, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]