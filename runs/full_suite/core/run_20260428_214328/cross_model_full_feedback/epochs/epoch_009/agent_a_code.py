def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = [(p[0], p[1]) for p in (observation.get("resources", []) or [])]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2): return abs(x1-x2) + abs(y1-y2)

    # Select a resource where we are ahead by a clear margin (obstacle-ignorant time)
    best = None
    for rx, ry in resources:
        if not inside(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        margin = do - ds
        if best is None or margin > best[0] or (margin == best[0] and ds < best[1]):
            best = (margin, ds, rx, ry)

    # If no clear advantage, fall back to closest resource to us
    if best is None:
        target = None
    else:
        margin, ds, rx, ry = best
        target = (rx, ry) if margin >= 2 else None
    if target is None:
        td = None; tr = None
        for rx, ry in resources:
            if not inside(rx, ry) or (rx, ry) in obstacles:
                continue
            d = manh(sx, sy, rx, ry)
            if td is None or d < td or (d == td and (rx, ry) < tr):
                td = d; tr = (rx, ry)
        target = tr

    # Choose move that reduces distance to target; if tie, avoids getting closer to opponent
    tx, ty = target if target is not None else (sx, sy)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            continue
        d_t = manh(nx, ny, tx, ty)
        d_o = manh(nx, ny, ox, oy)
        # Score: primary smaller distance to target; secondary larger distance from opponent; tertiary deterministic move order
        score = (d_t, -d_o, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]