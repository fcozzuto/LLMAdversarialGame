def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy  # Chebyshev for 8-way movement

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Predict opponent's likely target: closest remaining resource by distance-to-resource.
    best_opp_t = None
    best_opp_d = 10**9
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        d = dist(ox, oy, rx, ry)
        if d < best_opp_d:
            best_opp_d = d
            best_opp_t = (rx, ry)
    otx, oty = best_opp_t

    # One-step lookahead: choose move that maximizes our potential advantage on resources,
    # with added pressure to approach opponent's likely target when we fall behind.
    best_move = (0, 0)
    best_val = -10**18
    opp_to_own = dist(ox, oy, sx, sy)
    our_to_opp_t = dist(sx, sy, otx, oty)
    opp_to_opp_t = dist(ox, oy, otx, oty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Base: advantage potential over all resources.
        val = 0
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            od = dist(ox, oy, rx, ry)
            sd = dist(nx, ny, rx, ry)
            adv = od - sd
            if adv > 0:
                # Prefer resources where we are (and will remain) closer.
                val += adv * 10 - sd

        # If we're not competitive on the opponent's likely target, intercept directly.
        if our_to_opp_t > opp_to_opp_t:
            d_after = dist(nx, ny, otx, oty)
            val += (opp_to_opp_t - d_after) * 25 - d_after

        # Mild tie-break: reduce distance to opponent to discourage denier tactics near us.
        val -= dist(nx, ny, ox, oy) * 0.5

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]