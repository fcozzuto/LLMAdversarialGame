def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best_t = None
    best_key = None
    # pick a target where we are relatively earlier; tie-break by making opponent later
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # higher is better
        key = (opd - myd, -myd, -((tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If there are close "choke" resources for both, bias moves that reduce opponent lead
    def opp_lead_at(x, y, cell):
        cx, cy = cell
        return cheb(ox, oy, cx, cy) - cheb(x, y, cx, cy)

    best_mv = (0, 0)
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # primary: get to the chosen target
        myd = cheb(nx, ny, tx, ty)
        sc = (-myd, myd)
        # secondary: for other resources, favor moves that keep opponent behind on them
        worst = None
        for (rx, ry) in resources:
            if cheb(sx, sy, rx, ry) > 4 and cheb(ox, oy, rx, ry) > 4:
                continue
            lead = opp_lead_at(nx, ny, (rx, ry))
            if worst is None or lead > worst:
                worst = lead
        # worst here is actually best lead advantage for us; include it
        sc = (sc[0], sc[1], worst if worst is not None else 0, -abs(nx - ox) - abs(ny - oy))
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]