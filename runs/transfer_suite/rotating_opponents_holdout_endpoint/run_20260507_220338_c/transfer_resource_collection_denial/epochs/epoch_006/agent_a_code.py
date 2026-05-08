def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy))
    if not valid_moves:
        return [0, 0]

    # Pick a target we are (most) likely to reach first; if none, pick nearest resource.
    best = None
    best_gap = None
    for rx, ry in resources:
        gap = md(ox, oy, rx, ry) - md(sx, sy, rx, ry)
        if best_gap is None or gap > best_gap or (gap == best_gap and md(sx, sy, rx, ry) < md(sx, sy, best[0], best[1])):
            best_gap = gap
            best = (rx, ry)
    tx, ty = best
    if best_gap is not None and best_gap < 0:
        tx, ty = min(resources, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))

    # Score each move by improving our advantage toward the chosen target, with mild safety distance.
    best_move = valid_moves[0]
    best_score = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        my_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        adv = opp_d - my_d
        improvement = md(sx, sy, tx, ty) - my_d
        safety = md(nx, ny, ox, oy)
        score = (adv * 3) + (improvement * 0.8) + (safety * 0.05)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]