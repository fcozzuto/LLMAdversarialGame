def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx if dx >= dy else dy
    def adj_to_obstacle(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles: return 1
        return 0

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # If no legal moves (shouldn't happen), stay.
    def legal(nx, ny): return inb(nx, ny) and (nx, ny) not in obstacles

    # Choose a target resource that maximizes our likely advantage vs opponent.
    if resources:
        best_r = None; best_k = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we are closer to; and also those opponent is relatively far from.
            # Deterministic tie-breaking favors lower (rx,ry).
            k = (-(do - ds), do - ds, ds, rx, ry)  # larger (do-ds) => smaller first element
            if best_k is None or k < best_k:
                best_k = k; best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w // 2, h // 2)

    # Move toward target, but if it would hand the tempo to opponent, bias toward "blocking" positions near obstacles.
    best_move = (0, 0); best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): continue

        # Estimate who is closer to the current target after our move.
        ds_new = cheb(nx, ny, tx, ty)
        do_same = cheb(ox, oy, tx, ty)
        tempo = do_same - ds_new  # positive means we are closer than opponent

        # If we can't beat opponent on tempo, prefer staying near obstacles to constrain opponent routing.
        block = adj_to_obstacle(nx, ny)

        # Also keep some drift toward center for tie-breaking.
        center = cheb(nx, ny, w // 2, h // 2)
        key = (-(tempo + 2 * block), ds_new, center, nx, ny, dx, dy)
        if best_val is None or key < best_val:
            best_val = key; best_move = (dx, dy)

    return [best_move[0], best_move[1]]