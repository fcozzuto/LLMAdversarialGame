def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    if not resources:
        targets = [(w // 2, h // 2), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
        tx, ty = max(targets, key=lambda p: cheb(p[0], p[1], ox, oy))
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            key = (cheb(nx, ny, tx, ty),)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Choose the resource that best "wins" tempo for us.
        our_best = 10**9
        opp_best = 10**9
        win_best = -10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_self < our_best:
                our_best = d_self
            if d_opp < opp_best:
                opp_best = d_opp
            # Prefer being closer than opponent, and being decisively closer.
            win = (d_opp - d_self) - 0.15 * (d_self)
            if win > win_best:
                win_best = win
        # Also discourage positions where opponent is already very close to some resource.
        opp_threat = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        key = (-win_best, our_best, opp_threat, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]]