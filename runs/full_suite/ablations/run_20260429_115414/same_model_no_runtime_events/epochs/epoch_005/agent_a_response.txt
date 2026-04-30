def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles

    # Target selection: prefer resources where we are not worse; otherwise pick least-bad.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        s_t = cheb(sx, sy, rx, ry)
        o_t = cheb(ox, oy, rx, ry)
        adv = s_t - o_t  # smaller is better (we arrive earlier)
        # Extra preference for being closer than opponent and for centralish resources.
        center_bias = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
        key = (adv, s_t, center_bias, (rx * 131 + ry * 197) % 1000)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    # Move choice: maximize arrival advantage after the move, while avoiding near obstacles and
    # reducing opponent's ability to immediately improve toward the same target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        s_d = cheb(nx, ny, tx, ty)
        o_d = cheb(ox, oy, tx, ty)
        # Predict opponent improvement measure (how much they can reduce distance to target this turn).
        opp_best = -10**9
        for odx, ody in deltas:
            mx, my = ox + odx, oy + ody
            if not safe(mx, my):
                continue
            d2 = cheb(mx, my, tx, ty)
            opp_best = max(opp_best, (o_d - d2))  # reduction this turn
        # Obstacle proximity penalty
        prox = 0
        for ex in (nx - 1, nx, nx + 1):
            for ey in (ny - 1, ny, ny + 1):
                if (ex, ey) in obstacles:
                    prox += 1
        # Also discourage stepping closer to opponent to avoid being contested badly.
        dist_opp = cheb(nx, ny, ox, oy)

        # Score: higher is better
        score = (o_d - s_d) + 0.15 * opp_best + 0.05 * dist_opp - 0.25 * prox - 0.01 * (abs(dx) + abs(dy))
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]