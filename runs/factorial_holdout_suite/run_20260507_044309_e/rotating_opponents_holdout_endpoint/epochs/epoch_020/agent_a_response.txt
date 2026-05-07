def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    alpha = 0.65

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dsq(sx, sy, rx, ry)
        od = dsq(ox, oy, rx, ry)
        # Prefer resources where we're not much farther than opponent; closer is best.
        val = (sd - alpha * od, sd, rx, ry)
        if best is None or val < best[0]:
            best = (val, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # Choose move that best improves distance to target and blocks obvious denier captures.
    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to = dsq(nx, ny, tx, ty)
        # Immediate "race": compare distances to target after move.
        opp_to = dsq(ox, oy, tx, ty)
        # Slightly prefer positions where we are closer than opponent; else, still progress.
        race_pen = 0 if d_to <= opp_to else (d_to - opp_to)
        score = (d_to + 0.6 * race_pen, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move