def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    remaining = observation.get("remaining_resource_count", len(resources))

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources or remaining <= 0:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None; bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = -cheb((nx, ny), (tx, ty)) + 0.05 * cheb((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Pick a resource where we have/can gain an advantage over the opponent.
    best_r = None; best_adv = -10**18
    for rx, ry in resources:
        d_s = cheb((sx, sy), (rx, ry))
        d_o = cheb((ox, oy), (rx, ry))
        # Prefer resources where opponent isn't already much closer.
        adv = (d_o - d_s) - 0.01 * (d_s + d_o)
        if adv > best_adv:
            best_adv = adv; best_r = (rx, ry)

    tx, ty = best_r
    best = (0, 0, sx, sy); bestv = -10**18
    for dx, dy, nx, ny in legal:
        ds = cheb((nx, ny), (tx, ty))
        do = cheb((nx, ny), (ox, oy))
        # Move to reduce our distance to target and keep some distance from opponent.
        # Tie-break: also prefer positions that increase opponent's distance to our target.
        opp_ds = cheb((ox, oy), (tx, ty))
        cur_gap = (opp_ds - ds)  # larger means we're closer than opponent would be if we were there
        v = -ds + 0.02 * cur_gap + 0.03 * do
        if v > bestv:
            bestv = v; best = (dx, dy, nx, ny)

    return [best[0], best[1]]