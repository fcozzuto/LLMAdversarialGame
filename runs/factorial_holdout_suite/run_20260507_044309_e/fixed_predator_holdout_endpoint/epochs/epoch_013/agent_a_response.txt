def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1 - ox + sx) // 2, (h - 1 - oy + sy) // 2
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in cand:
            v = -manhattan(nx, ny, tx, ty) - 0.01 * manhattan(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    best_move = None
    best_val = -10**18
    for dx, dy, nx, ny in cand:
        # Evaluate best resource from this neighbor.
        best_r = -10**18
        for rx, ry in resources:
            sd = manhattan(nx, ny, rx, ry)
            od = manhattan(ox, oy, rx, ry)
            # Strongly prefer resources we can reach no later than opponent.
            if sd <= od:
                v = 2000 - 10 * sd + 3 * (od - sd)
            else:
                # Still consider resources where we are "closest" among contested ones.
                v = 200 - sd - 2 * (sd - od)
            # Light preference to avoid clustering far away.
            v -= 0.001 * (manhattan(nx, ny, ox, oy))
            if v > best_r:
                best_r = v
        if best_r > best_val:
            best_val = best_r
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move else [0, 0]