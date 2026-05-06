def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def center_score(x, y):
        cx = (w - 1) / 2.0; cy = (h - 1) / 2.0
        dx = abs(x - cx); dy = abs(y - cy)
        return -(dx + dy)

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Prefer center; avoid stepping adjacent/onto opponent line-of-pressure.
            adj = max(abs(nx - ox), abs(ny - oy)) <= 1
            sc = center_score(nx, ny) - (1.5 if adj else 0) + (0.1 if (nx, ny) == (sx, sy) else 0)
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose move that maximizes relative advantage to a resource (we want ours closer than opponent's).
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        opp_adj = max(abs(nx - ox), abs(ny - oy)) <= 1
        # Evaluate best resource under this move.
        best_adv = None
        best_raw = None
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            adv = d_op - d_me  # positive means we are closer than opponent
            raw = -d_me  # prefer lower absolute distance
            if best_adv is None or adv > best_adv or (adv == best_adv and raw > best_raw):
                best_adv = adv; best_raw = raw
        # If we can't get ahead, still try to reduce our distance; center to avoid getting herded.
        sc = 4.0 * best_adv + 1.0 * best_raw + 0.15 * center_score(nx, ny) - (2.0 if opp_adj else 0)
        # Mild preference to avoid wasting moves when already best-positioned
        if sc == (best[0] if best else None):
            if (nx, ny) == (sx, sy):
                sc += 0.01
        if best is None or sc > best[0]:
            best = (sc, dx, dy)
    return [best[1], best[2]] if best else [0, 0]