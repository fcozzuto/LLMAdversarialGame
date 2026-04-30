def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        tx, ty = cx, cy
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                nx, ny = sx, sy
                dx, dy = 0, 0
            key = (cheb(nx, ny, tx, ty), cheb(nx, ny, cx, cy), dx, dy)
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return list(best if best is not None else (0, 0))

    resources_set = {(r[0], r[1]) for r in resources}
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ndx, ndy = dx, dy
        if not inb(nx, ny) or (nx, ny) in occ:
            nx, ny = sx, sy
            ndx, ndy = 0, 0

        # Offensive: how much closer we are than opponent for our best resource.
        best_adv = -10**9
        best_sd = 10**9
        best_od = 10**9

        # Defensive: how much better opponent is than us for their best resource.
        best_opp_adv = -10**9

        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and od < best_od))):
                best_adv, best_sd, best_od = adv, sd, od
            opp_adv = sd - od
            if opp_adv > best_opp_adv:
                best_opp_adv = opp_adv

        capture_bonus = 500 if (nx, ny) in resources_set else 0
        central_pen = cheb(nx, ny, cx, cy)
        # Maximize: capture/offense advantage, minimize vulnerability and distance.
        score_num = capture_bonus + best_adv * 50 - best_opp_adv * 25 - best_sd
        # Deterministic tie-breakers.
        key = (-score_num, best_sd, central_pen, best_od, ndx, ndy)
        if best_key is None or key < best_key:
            best_key = key
            best = (ndx, ndy)

    return [int(best[0]), int(best[1])]