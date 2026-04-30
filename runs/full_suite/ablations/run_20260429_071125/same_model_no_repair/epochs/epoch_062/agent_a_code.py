def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    t = observation.get("turn_index", 0)

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    if not res:
        cx, cy = w - 1, h - 1
        cx, cy = (cx, cy) if (t % 2 == 0) else ((w // 2), (h // 2))
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, cx, cy) + 0.1 * cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Pick a target resource that we can reach well, while making it harder for the opponent.
    my_rem = observation.get("remaining_resource_count", len(res))
    denial = 0.35 if my_rem <= 6 else 0.20
    best_r = None
    best_rv = -10**18
    for rx, ry in res:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Mild bias to move towards higher x then y to break ties deterministically.
        tv = -md + denial * od + 0.01 * rx - 0.005 * ry
        if tv > best_rv or (tv == best_rv and (rx, ry) < best_r):
            best_rv, best_r = tv, (rx, ry)

    rx, ry = best_r
    # Evaluate each move towards the target with a small denial term.
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in legal:
        md2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)  # opponent position unchanged this turn
        # If we're very close, prioritize securing: small bonus for stepping onto target.
        onto = 1.0 if (nx == rx and ny == ry) else 0.0
        v = -md2 + denial * od2 + onto - 0.02 * cheb(nx, ny, ox, oy)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]