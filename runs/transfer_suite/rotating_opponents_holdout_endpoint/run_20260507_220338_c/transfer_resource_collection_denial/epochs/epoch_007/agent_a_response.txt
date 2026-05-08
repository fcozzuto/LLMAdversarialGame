def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate this move by the best resource we can contest next turn.
        # Bias away from opponent's current row to counter sweep-like behavior.
        best = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # higher is better: we want do - ds large; row distance adds deterministic tie-bias
            val = (do - ds) * 4 - abs(ry - oy)
            if best is None or val > best:
                best = val
        if best is None:
            continue

        if best_val is None or best > best_val:
            best_val = best
            best_move = [dx, dy]
        elif best == best_val:
            # deterministic tie-break: prefer smaller ds to closest contested resource
            cur_best_ds = None
            for rx, ry in resources:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                val = (do - ds) * 4 - abs(ry - oy)
                if val == best:
                    if cur_best_ds is None or ds < cur_best_ds:
                        cur_best_ds = ds
            best_ds = None
            bx, by = sx + best_move[0], sy + best_move[1]
            for rx, ry in resources:
                ds = md(bx, by, rx, ry)
                do = md(ox, oy, rx, ry)
                val = (do - ds) * 4 - abs(ry - oy)
                if val == best_val:
                    if best_ds is None or ds < best_ds:
                        best_ds = ds
            if cur_best_ds is not None and (best_ds is None or cur_best_ds < best_ds):
                best_move = [dx, dy]

    return best_move if best_val is not None else [0, 0]