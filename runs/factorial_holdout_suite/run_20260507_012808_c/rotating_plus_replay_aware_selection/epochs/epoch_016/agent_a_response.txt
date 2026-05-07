def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best_res = None
    best_val = None
    for r in resources:
        rx, ry = r[0], r[1]
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Primary: be closer than opponent (margin do-ds). Secondary: break ties by less aligned.
        align = min(abs(ry - oy), abs(rx - ox))
        val = (do - ds, -align, -ds, rx, ry)
        if best_val is None or val > best_val:
            best_val = val
            best_res = (rx, ry)

    if best_res is None:
        # Fallback: head toward nearest corner-ish alternating by turn for determinism.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        target = corners[observation.get("turn_index", 0) % 4]
    else:
        target = best_res

    tx, ty = target
    best_move = None
    best_mv_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Prefer moves that increase capture margin; then reduce distance; then prefer not moving away.
        mv_val = (do2 - ds2, -ds2, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_mv_val is None or mv_val > best_mv_val:
            best_mv_val = mv_val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]