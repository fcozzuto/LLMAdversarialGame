def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res_list = [tuple(r) for r in resources]
    best_move = (0, 0); best_val = -10**18

    for dx, dy in moves:
        nx = sx + dx; ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        move_best = -10**18
        for rx, ry in res_list:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            swing = do - ds  # positive if we can arrive first
            # Prefer large swing, shorter distance, and earlier in value-breaking by coordinates.
            val = swing * 10000 - ds * 40 - (rx * 0.01 + ry * 0.02)
            if val > move_best:
                move_best = val

        # Small bias toward reducing distance to opponent to prevent opponent steals.
        do_now = cheb(nx, ny, ox, oy)
        move_val = move_best - do_now * 0.1

        if move_val > best_val:
            best_val = move_val; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]