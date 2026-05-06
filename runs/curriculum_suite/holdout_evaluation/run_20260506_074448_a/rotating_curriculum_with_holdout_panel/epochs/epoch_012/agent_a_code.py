def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def edge_score(x, y):
        # prefer interior (opponent patrols edges)
        d = x
        if w - 1 - x < d:
            d = w - 1 - x
        if y < d:
            d = y
        if h - 1 - y < d:
            d = h - 1 - y
        return -d  # smaller d (closer to edge) -> worse

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate move by best "win" over opponent on any resource this turn
        my_best_myd = None
        my_best_adv = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if my_best_adv is None or adv > my_best_adv or (adv == my_best_adv and myd < my_best_myd):
                my_best_adv = adv
                my_best_myd = myd

        if my_best_adv is None:
            key = (-10**9, 0, 0)  # fallback
        else:
            # Prefer higher advantage, then closer to the resource, then interior.
            key = (-(my_best_adv * 1000), my_best_myd, -edge_score(nx, ny), dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move