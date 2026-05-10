def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        ax -= bx
        if ax < 0:
            ax = -ax
        ay -= by
        if ay < 0:
            ay = -ay
        return ax + ay

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy

        best_r_for_move = None
        best_r_val = -10**18

        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we can take sooner, and that are less attractive to opponent
            val = (od - sd) * 1000 - sd
            # Small deterministic tie-breaker + parity to avoid cycling
            val += ((sd + rx + ry) % 2) * 3
            val += -(rx * 7 + ry * 11) * 1e-6
            if val > best_r_val:
                best_r_val = val
                best_r_for_move = (rx, ry)

        # Also consider whether opponent is closer to any resource (risk)
        opp_best = 10**9
        for rx, ry in resources:
            d = man(ox, oy, rx, ry)
            if d < opp_best:
                opp_best = d

        score = best_r_val - opp_best
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move