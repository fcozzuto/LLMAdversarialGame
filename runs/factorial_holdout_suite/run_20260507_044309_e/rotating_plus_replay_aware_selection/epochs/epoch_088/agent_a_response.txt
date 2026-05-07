def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    move_order = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if resources:
        best_res = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner (small ds) and opponent later (large do).
            # Tie-break deterministically by coordinates.
            key = (ds - do, ds, -do, rx, ry)
            if best_res is None or key < best_res[0]:
                best_res = (key, (rx, ry))
        tx, ty = best_res[1]
        curd = cheb(sx, sy, tx, ty)
    else:
        # No visible resources: drift to a deterministic "safe" point near center.
        tx, ty = w // 2, h // 2
        curd = cheb(sx, sy, tx, ty)

    best_move = [0, 0]
    best_key = None
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # New heuristic vs previous: evaluate relative progress vs opponent along the same target.
        adv = (cheb(ox, oy, tx, ty) - nd) - (curd - cheb(ox, oy, tx, ty))
        # Also prefer staying away from obstacles by discouraging moves that reduce clearance poorly.
        clearance = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                    clearance -= 1
        key = (nd, -adv, clearance, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]