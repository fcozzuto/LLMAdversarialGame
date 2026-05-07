def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    ti = int(observation.get("turn_index", 0) or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def is_free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose a resource we are likely to reach first: self_dist - 0.6*opp_dist (lower is better)
    best = None
    for tx, ty in resources:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        # Tie-breaker: prefer earlier progress along the line to reduce dithering
        prog = (abs(tx - sx) + abs(ty - sy))
        val = sd - 0.6 * od + 0.001 * ((ti + tx * 3 + ty * 5 + prog) % 101)
        if best is None or val < best[0] or (val == best[0] and (tx, ty) < (best[1], best[2])):
            best = (val, tx, ty)

    tx, ty = best[1], best[2]

    # Take the best one-step move by minimizing estimated "arrival advantage"
    best_step_val = None
    best_step_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, tx, ty)
        # Encourage getting closer; discourage stepping into worse parity by small deterministic bias
        val = sd2 - 0.6 * od2 + 0.002 * ((nx * 7 + ny * 11 + ti) % 97)
        if best_step_val is None or val < best_step_val or (val == best_step_val and (dx, dy) < best_step_move):
            best_step_val = val
            best_step_move = (dx, dy)

    return [int(best_step_move[0]), int(best_step_move[1])]