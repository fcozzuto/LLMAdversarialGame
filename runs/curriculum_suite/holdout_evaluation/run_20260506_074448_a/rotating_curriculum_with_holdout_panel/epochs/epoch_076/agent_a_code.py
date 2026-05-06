def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = [(dx, dy) for dx in dxs for dy in dys]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Select a deterministic target based on tempo advantage we can create now.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        oppd = man(ox, oy, rx, ry)
        tempo = oppd - myd  # positive => we are closer (earlier)
        cent = -(abs(rx - cx) + abs(ry - cy))
        # Prefer clear tempo wins; otherwise prefer closer-to-center and shorter my distance.
        key = (-(tempo >= 2), -tempo, cent, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    # Evaluate all legal deltas deterministically; pick best.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us; emulate for scoring
        myd = man(nx, ny, tx, ty)
        oppd = man(ox, oy, tx, ty)
        tempo_after = oppd - myd

        # Add opportunistic switch: if a different resource yields better tempo after the move, consider it.
        best_alt = None
        best_alt_tempo = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            alt_myd = man(nx, ny, rx, ry)
            alt_oppd = man(ox, oy, rx, ry)
            alt_tempo = alt_oppd - alt_myd
            if best_alt is None or alt_tempo > best_alt_tempo or (alt_tempo == best_alt_tempo and (alt_myd, rx, ry) < (best_alt_myd, best_alt[0], best_alt[1])):
                best_alt = (rx, ry, alt_myd)
                best_alt_tempo = alt_tempo
                best_alt_myd = alt_myd
        # Score combines keeping tempo advantage and ensuring we move toward the best achievable resource.
        target_bias = man(nx, ny, tx, ty) - man(sx, sy, tx, ty)
        score = (
            -(tempo_after >= 2),  # force tempo wins when possible
            -max(tempo_after, best_alt_tempo),  # maximize achievable tempo
            abs(nx - ox) + abs(ny - oy),  # avoid getting too close to opponent unintentionally
            myd,  # closer to chosen target
            target_bias,  # don't step away
            nx, ny, dx, dy
        )
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]