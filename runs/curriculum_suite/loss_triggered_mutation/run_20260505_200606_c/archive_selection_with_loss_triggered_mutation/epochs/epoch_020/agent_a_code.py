def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return (x, y) not in obstacles
    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy
    def dist1(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    # Pick a deterministic target
    tx = ty = None
    best_adv = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        ds = dist2(sx, sy, rx, ry)
        do = dist2(ox, oy, rx, ry)
        adv = do - ds
        # tie-breaker by resource position to keep deterministic
        if adv > best_adv or (adv == best_adv and (rx, ry) < (tx, ty) if tx is not None else True):
            best_adv = adv
            tx, ty = rx, ry
    if tx is None:
        tx, ty = (w // 2), (h // 2)

    # If no clear advantage, still move toward closest resource
    if resources and best_adv <= 0:
        best_d = 10**18
        for r in resources:
            rx, ry = r[0], r[1]
            ds = dist2(sx, sy, rx, ry)
            if ds < best_d or (ds == best_d and (rx, ry) < (tx, ty)):
                best_d = ds
                tx, ty = rx, ry

    # Evaluate each valid move greedily with an "intercept" repulsion near opponent
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        d_to_t = dist2(nx, ny, tx, ty)

        # Encourage reaching target, and deny opponent nearby
        d_opp = dist1(nx, ny, ox, oy)
        opp_repulse = 0
        if d_opp <= 2:
            opp_repulse = 8 - 4 * d_opp

        # If we are moving toward the target, estimate resulting advantage vs opponent for that same target
        opp_d_to_t = dist2(ox, oy, tx, ty)
        self_d_to_t = d_to_t
        adv_term = opp_d_to_t - self_d_to_t  # higher is better

        # Prefer slightly increasing distance from opponent generally to avoid being collected-contested
        general_opp = dist2(nx, ny, ox, oy)

        val = (1000 - d_to_t) + 0.7 * adv_term + opp_repulse + 0.01 * general_opp
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]