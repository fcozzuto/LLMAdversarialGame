def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    def move_score(nx, ny, tx, ty):
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        return (od - sd) * 100 - sd

    best_move = (0, 0)
    best_val = -10**18

    if resources:
        # Pick target resource that we can reach relatively sooner than opponent
        best_t = None
        best_key = None
        for rx, ry in resources:
            sd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od - sd, -sd, -od, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacle_set:
                continue
            val = move_score(nx, ny, tx, ty)
            # small tie-break: prefer staying unblocked and closer to target
            sd = cheb(nx, ny, tx, ty)
            if val > best_val or (val == best_val and (sd < cheb(x, y, tx, ty) or (nx, ny) < best_move)):
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: deterministically reposition to deny/preserve by moving away from opponent while improving position
    # Prefer center while increasing chebyshev distance to opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_center_key = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacle_set:
            continue
        dist_opp = cheb(nx, ny, ox, oy)
        dist_ctr = cheb(nx, ny, cx, cy)
        key = (dist_opp, -dist_ctr, -dx, -dy, nx, ny)
        if best_center_key is None or key > best_center_key:
            best_center_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]