def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles") or [])

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    # Choose a target resource where we have largest (opp_dist - self_dist) advantage.
    best_t = None
    best_adv = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds
        key = (adv, -ds, rx, ry)
        if best_adv is None or key > best_adv:
            best_adv = key
            best_t = (rx, ry)

    if best_t is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            dcent = dist(nx, ny, cx, cy)
            dopp = dist(nx, ny, ox, oy)
            v = (dopp - dcent)  # keep away from opponent while moving toward center
            k = (v, -dopp, dx + 2 * dy)
            if k > best:
                best = k
        return [best[1], best[2]]

    rx, ry = best_t
    # Choose move that maximizes advantage after moving toward the target.
    best_move = (-(10**9), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = dist(nx, ny, rx, ry)
        do2 = dist(ox, oy, rx, ry)
        adv2 = do2 - ds2
        # Prefer reducing our distance; use deterministic tie-breaks.
        v = (adv2 * 10) - ds2
        k = (v, -ds2, nx, ny)
        if k > best_move:
            best_move = (v, dx, dy)
    return [best_move[1], best_move[2]]