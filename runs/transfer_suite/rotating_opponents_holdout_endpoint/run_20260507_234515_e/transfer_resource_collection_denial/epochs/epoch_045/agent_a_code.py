def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((p[0], p[1]))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources or observation.get("turns_remaining", 0) <= 1:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            key = (cheb(nx, ny, cx, cy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_best = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # maximize (opp_d - my_d); tie-break toward smaller my_d
            adv = opp_d - my_d
            cand = (adv, -my_d)
            if my_best is None or cand > my_best:
                my_best = cand
        # small additional preference to move closer to center only if score ties
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_d = cheb(nx, ny, cx, cy)
        key = (-my_best[0], my_best[1] * -1, center_d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]