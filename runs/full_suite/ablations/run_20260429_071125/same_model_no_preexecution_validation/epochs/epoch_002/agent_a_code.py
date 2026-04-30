def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    if not resources:
        tx, ty = ox, oy
    else:
        # Choose resources where we are (strictly) closer than the opponent; otherwise avoid likely contested ones.
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            contested = 0 if myd < opd else 1
            # Secondary: prefer smaller lead gap in our favor and closer overall.
            # Then lexicographic for determinism.
            key = (contested, myd, opd - myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        if best is None:
            tx, ty = ox, oy
        else:
            tx, ty = best[1], best[2]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # Move to minimize distance to target; keep opponent farther unless it costs too much.
        # Encode as: (primary d_t, secondary -d_o, tie-break lex).
        score = (d_t, -d_o, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]