def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0, -10**9]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not passable(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            val = -d + (0.05 * cheb(nx, ny, ox, oy))
            if val > best[2]:
                best = [dx, dy, val]
        return [best[0], best[1]]

    # Choose a "deny-or-race" target deterministically.
    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # If opponent is closer, only chase if we are extremely close (intercept attempt).
        if our_d > opp_d:
            if our_d <= 1:
                val = (opp_d - our_d) * 5 - our_d * 0.2
            else:
                val = -10**6 + (opp_d - our_d)  # deprioritize
        else:
            val = (opp_d - our_d) * 10 - our_d * 0.2
        # Tie-break toward nearer resources and toward blocking (stay farther from opponent when possible).
        val += -0.02 * our_d + 0.01 * cheb(sx, sy, ox, oy)
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r

    # Evaluate immediate move by improving the advantage at the chosen target, with obstacle safety.
    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Prefer reducing