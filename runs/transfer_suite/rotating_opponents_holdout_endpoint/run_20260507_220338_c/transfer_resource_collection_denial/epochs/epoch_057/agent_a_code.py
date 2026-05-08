def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target: first prefer resources we can reach first; otherwise maximize "lead".
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # behind_check: we are farther => likely steal; prioritize where opponent advantage is smallest.
        lead = od - sd  # positive if we are closer
        # prefer closer targets but also avoid giving opponent huge advantage
        key = (sd, -lead) if od <= sd + 1 else (sd, -(lead + 2))
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # If already on a resource, stay (collect).
    if sx == tx and sy == ty:
        return [0, 0]

    # Choose best one-step move that decreases distance to target, avoiding obstacles.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                moves.append((dx, dy))

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    best_move = (None, None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        self_d = man(nx, ny, tx, ty)
        # discourage moves that put us adjacent/close to the opponent relative to the same target
        opp_d = man(ox, oy, tx, ty)
        # small tie-break for advancing along both axes (deterministic)
        diag_adv = -(dx != 0 and dy != 0)
        score = (self_d, -opp_d, diag_adv, dx, dy)
        if best_move[0] is None or score < best_move[0]:
            best_move = (score, dx, dy)

    if best_move[1] is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]