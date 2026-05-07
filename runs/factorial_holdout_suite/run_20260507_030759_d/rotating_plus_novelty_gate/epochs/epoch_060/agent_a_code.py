def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res_list = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = set(tuple(r) for r in res_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))

    if not legal:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    if not resources:
        # Drift to keep options open: move that maximizes distance from opponent while valid
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dopp = abs(nx - ox) + abs(ny - oy)
            if best is None or (dopp, -abs(nx - (w - 1 - ox)) - abs(ny - (h - 1 - oy))) > best:
                best = (dopp, -abs(nx - (w - 1 - ox)) - abs(ny - (h - 1 - oy)))
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose move that maximizes advantage over opponent for the best reachable resource.
    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Advantage: opponent is farther than we are (opp_d - self_d) -> bigger is better
        best_adv = None
        best_self_d = None
        for rx, ry in resources:
            self_d = manh(nx, ny, rx, ry)
            opp_d = manh(nx, ny, ox, oy)
            adv = opp_d - self_d
            if best_adv is None or (adv, -self_d) > (best_adv, -best_self_d):
                best_adv = adv
                best_self_d = self_d
        # Also prefer moves that reduce our own distance to any resource in case of tie.
        tie2 = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        cand = (best_adv, -tie2, -dx, -dy)
        if best is None or cand > best:
            best = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]