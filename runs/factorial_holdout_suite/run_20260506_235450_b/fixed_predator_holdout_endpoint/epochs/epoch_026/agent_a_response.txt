def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target resources that are far from the opponent; then make them as close as possible for us.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        # prioritize: maximize opponent distance, then minimize our distance, then tie-break deterministically
        val = (od, -sd, -rx, -ry)
        if best is None or val > best[0]:
            best = (val, rx, ry)

    _, tx, ty = best

    # Choose the next move that best reduces distance to chosen target while not letting the move go into blocked cells.
    best_move = [0, 0]
    best_score = None
    order = moves  # deterministic order
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        self_d = md(nx, ny, tx, ty)
        opp_d = md(nx, ny, ox, oy)
        score = (-self_d, opp_d, dx, dy)  # primary: closer to target; secondary: keep farther from opponent
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if not inb(sx, sy):
        return [0, 0]
    return best_move