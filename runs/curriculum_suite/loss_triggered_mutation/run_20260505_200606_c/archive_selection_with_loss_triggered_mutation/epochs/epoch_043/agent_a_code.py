def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_key = None
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer moves that improve advantage to the most favorable resource
            local_best = None
            for rx, ry in resources:
                sd = md(nx, ny, rx, ry)
                od = md(ox, oy, rx, ry)
                key = (od - sd, -sd, rx, ry)  # maximize advantage, then closeness, deterministic tie
                if local_best is None or key > local_best:
                    local_best = key
            if local_best is None:
                continue
            # Also break ties by staying closer to opponent slightly (helps contention control)
            tie = (local_best[0], local_best[1], -md(nx, ny, ox, oy), dx, dy)
            if best_key is None or tie > best_key:
                best_key = tie
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: patrol toward the far corner relative to opponent's edge bias
    tx = w - 1 if ox < w // 2 else 0
    ty = h - 1 if oy < h // 2 else 0
    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d1 = md(nx, ny, tx, ty)
        d2 = md(nx, ny, ox, oy)
        # Prefer moving closer to target corner, and also slightly away from opponent
        key = (-d1, d2, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]