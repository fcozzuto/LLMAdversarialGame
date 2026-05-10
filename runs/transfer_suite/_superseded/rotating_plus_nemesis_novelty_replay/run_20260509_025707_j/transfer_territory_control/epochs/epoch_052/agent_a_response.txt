def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    obs_set = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    myc = observation.get("self_territory_count", 0)
    opc = observation.get("opponent_territory_count", 0)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    # Immediate flip if we can enter opponent territory this turn
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        enter_opp = (nx, ny) in opp_set
        if enter_opp:
            # If multiple, prefer the one closest to center (deny their center claim)
            sc = abs(nx - cx) + abs(ny - cy)
            if best is None or sc < best[0]:
                best = (sc, dx, dy)
    if best is not None:
        return [best[1], best[2]]

    # Otherwise, choose an opponent cell to approach/harass; bias toward center control.
    prefer_front = (myc < opc)
    # If we are not behind, still contest center but slightly prefer edge pressure.
    front_w = 2.0 if prefer_front else 1.2
    edge_w = 0.3 if prefer_front else 0.8

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target = None
    for ox, oy in opp_set:
        d = manh(sx, sy, ox, oy)
        center_bias = manh(ox, oy, cx, cy)
        edge_bias = min(ox, (w - 1) - ox) + min(oy, (h - 1) - oy)
        sc = d + front_w * center_bias - edge_w * edge_bias
        if target is None or sc < target[0]:
            target = (sc, ox, oy)
    if target is None:
        return [0, 0]
    _, tx, ty = target

    # Pick the move that best reduces distance to target; tie-break by moving toward center.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dcur = manh(nx, ny, tx, ty)
        cen = manh(nx, ny, cx, cy)
        # Small deterministic tie-break: lexicographic on (dx,dy)
        tieb = (dx, dy)
        sc = (dcur, cen, tieb)
        if best is None or sc < best[0]:
            best = (sc, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]