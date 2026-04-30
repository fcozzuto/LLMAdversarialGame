def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best_tval = -10**18

    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        center = cheb(rx, ry, cx, cy)
        # Strongly prioritize resources where we are closer than opponent; otherwise still move toward good options.
        tval = (do - ds) * 20 - ds * 2 - center * 0.25
        if tval > best_tval:
            best_tval = tval
            best_target = (rx, ry)

    if best_target is None:
        tx, ty = int(round(cx)), int(round(cy))
    else:
        tx, ty = best_target

    best_move = (0, 0)
    best_mval = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Value: improve our distance to target and deny opponent by reducing advantage gap.
        ds_now = cheb(nx, ny, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        center_now = cheb(nx, ny, cx, cy)
        move_cost = 0.05 * ((dx != 0) or (dy != 0))
        mval = (do_now - ds_now) * 20 - ds_now * 2 - center_now * 0.25 - move_cost
        # Tie-break deterministically toward staying closer to center; then toward smaller dx, then smaller dy.
        if mval > best_mval:
            best_mval = mval
            best_move = (dx, dy)
        elif mval == best_mval:
            if cheb(nx, ny, cx, cy) < cheb(sx + best_move[0], sy + best_move[1], cx, cy):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]