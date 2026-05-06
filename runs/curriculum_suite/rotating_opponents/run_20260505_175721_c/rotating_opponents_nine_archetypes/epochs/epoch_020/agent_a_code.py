def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            key = (cheb(nx, ny, cx, cy), 0, dx, dy)
            if best is None or key < best:
                best = key
        return [best[2], best[3]] if best else [0, 0]

    def target_value(rx, ry, px, py):
        ds = cheb(px, py, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we can get there at least as well as opponent,
        # and where opponent is relatively farther after we move.
        return (do - ds) * 10 - ds

    best_key = None
    best_move = (0, 0)

    # Evaluate each immediate move by the best resource it would give us (deterministic, local).
    # Tie-breakers: prefer higher advantage, then closer to that resource, then toward center.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        best_for_move = None
        best_ds = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            val = target_value(rx, ry, nx, ny)
            key = (-val, ds, cheb(ox, oy, rx, ry), rx, ry)
            if best_for_move is None or key < best_for_move:
                best_for_move = key
                best_ds = ds
        # Overall move key: maximize value => minimize -value via key; add center pressure to break ties.
        move_key = (best_for_move[0], best_for_move[1], best_for_move[2], cheb(nx, ny, cx, cy), dx, dy)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]