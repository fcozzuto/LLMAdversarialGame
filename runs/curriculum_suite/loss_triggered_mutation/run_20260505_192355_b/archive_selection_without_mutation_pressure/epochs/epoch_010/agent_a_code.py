def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set()
    obs_list = observation.get("obstacles") or []
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    resources = observation.get("resources") or []
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_resources = None
    if resources:
        best_resources = None
        best_key = None
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            opd = man(ox, oy, rx, ry)
            key = (myd - 0.7 * opd, myd, rx + ry)
            if best_key is None or key < best_key:
                best_key = key
                best_resources = (rx, ry)

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if best_resources is not None:
            rx, ry = best_resources
            myd2 = man(nx, ny, rx, ry)
            opd2 = man(ox, oy, rx, ry)
            target_term = myd2 - 0.75 * opd2
        else:
            target_term = man(nx, ny, ox, oy)
        opp_term = man(nx, ny, ox, oy)
        # Prefer smaller target_term; then prefer getting closer to opponent; then stay.
        score = (target_term, opp_term, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move