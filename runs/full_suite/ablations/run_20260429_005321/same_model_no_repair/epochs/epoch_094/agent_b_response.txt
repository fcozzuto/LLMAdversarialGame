def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obst(x, y):
        c = 0
        for dx, dy in adj:
            if (x + dx, y + dy) in obst:
                c += 1
        return c

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        # Choose move that maximizes immediate advantage for the best resource we could realistically reach.
        best_dxdy = None
        best_score = -10**18
        for dx, dy, nx, ny in legal:
            # Evaluate best target from next position.
            best_adv = -10**18
            best_d = 10**9
            best_rob = 10**9
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Advantage: we want (opponent distance - our distance).
                adv = (od - sd)
                if sd == 0:
                    adv += 20  # strong grab
                rob = near_obst(rx, ry)
                # Tie-break: closer target and safer area.
                key = (adv, -sd, -rob)
                cur = (adv, -sd, -rob)
                if cur > (best_adv, -best_d, -best_rob):
                    best_adv, best_d, best_rob = adv, sd, rob
            score = best_adv * 10 - best_d - 0.35 * near_obst(nx, ny) - 0.05 * cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score, best_dxdy = score, (dx, dy)
        return [best_dxdy[0], best_dxdy[1]]

    # No resources: deterministic pressure toward opponent side while avoiding obstacles.
    tx, ty = (w - 1 if ox < w - 1 else 0), (h - 1 if oy < h - 1 else 0)
    best_dxdy = (0, 0)
    bestv = 10**18
    for dx, dy, nx, ny in legal:
        v = cheb(nx, ny, tx, ty) + 0.65 * cheb(nx, ny, (ox, oy)[0], (ox, oy)[1]) * 0.1 + 0.35 * near_obst(nx, ny)
        if v < bestv:
            bestv, best_dxdy = v, (dx, dy)
    return [best_dxdy[0], best_dxdy[1]]