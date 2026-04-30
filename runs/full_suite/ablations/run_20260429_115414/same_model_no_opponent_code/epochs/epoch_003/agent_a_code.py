def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)
    rx_list = [(int(x), int(y)) for x, y in resources]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer a resource where we beat opponent (by distance advantage); otherwise race closest.
    best = None
    best_key = None
    for rx, ry in rx_list:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # maximize (do-ds): positive means we are closer; tie-break: smaller ds; then deterministic by coords
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (w // 2, h // 2)

    # If target is an obstacle (shouldn't happen), fallback to center-ish.
    if (tx, ty) in obs:
        tx, ty = w // 2, h // 2

    # Heuristic step selection: minimize our distance; avoid obstacles; try to move away from opponent slightly.
    best_move = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d_to = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            # Main: distance to target. Secondary: keep away from opponent to reduce contest.
            # Additional: prefer positions that improve our relative advantage to target.
            opp_d_to = cheb(ox, oy, tx, ty)
            our_d = d_to
            rel = opp_d_to - our_d
            score = ( -d_to, rel, d_opp, -nx, -ny )
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]