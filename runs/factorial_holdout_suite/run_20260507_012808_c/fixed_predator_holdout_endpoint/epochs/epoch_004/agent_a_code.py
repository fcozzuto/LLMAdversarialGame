def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not resources:
        # Drift to quadrant center for deterministic symmetry breaking
        tx, ty = (w - 1) // 4, (h - 1) // 4
        best = (10**18, 0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            cand = (d, dx, dy)
            if cand < best: best = cand
        return [best[1], best[2]]

    ox, oy = observation["opponent_position"]

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Evaluate each move by the best resource we could contest from next position.
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        cur_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer nearer-to-us and farther-from-opponent; also bias toward immediate reach.
            val = (od - sd) * 100 - sd
            if val > cur_best:
                cur_best = val
        # Tie-break deterministically by preferring diagonal, then lexicographic (dx,dy).
        cand = (cur_best, 1 if (dx != 0 and dy != 0) else 0, -abs(dx) - abs(dy), -dx, -dy)
        if cand > (best_val, 0, 0, 0, 0):
            best_val = cand[0]
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]