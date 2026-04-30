def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # If no resources, just drift toward the center and slightly away from opponent obstacles pressure.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            key = (cheb(nx, ny, cx, cy), -cheb(nx, ny, ox, oy), nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Obstacle vicinity penalty
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in occ:
                    adj_pen += 3 if (ax == 0 or ay == 0) else 2

        # Choose the resource that gives best "take it first" advantage from this move
        best_val_for_move = -10**18
        best_sub_tie = None
        for rx, ry in resources:
            dself = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Prefer grabbing resource if we can be earlier; also lower our own distance
            val = (dop - dself) * 7 - dself
            if dself == 0:
                val += 50
            # If opponent is closer/equal, reduce priority
            if dop <= dself:
                val -= 4
            sub_tie = (-(val), dself, dop, rx, ry)
            if val > best_val_for_move or (val == best_val_for_move and best_sub_tie < best_sub_tie):
                best_val_for_move = val
                best_sub_tie = sub_tie

        # Maximize overall value; tie-break deterministically by position
        key = (-best_val_for_move + adj_pen, cheb(nx, ny, ox, oy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]