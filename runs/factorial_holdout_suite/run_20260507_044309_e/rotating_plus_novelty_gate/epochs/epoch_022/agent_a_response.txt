def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid_targets = [(rx, ry) for (rx, ry) in resources if inb(rx, ry)]
    if not valid_targets:
        return [0, 0]

    # Take immediately if adjacent
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            for rx, ry in valid_targets:
                if nx == rx and ny == ry:
                    return [dx, dy]

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # For this candidate move, choose the resource with best "win probability" proxy.
        best_res_key = None
        for rx, ry in valid_targets:
            myd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources I reach strictly earlier; if tie, prefer where opponent is later.
            # Key is lexicographic for determinism.
            res_key = (0 if myd < od else 1, myd - od, myd, od)
            if best_res_key is None or res_key < best_res_key:
                best_res_key = res_key

        if best_key is None or best_res_key < best_key:
            best_key = best_res_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]