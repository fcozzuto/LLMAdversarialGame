def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    # Predict opponent's most likely target (nearest by Manhattan distance).
    opp_target = None
    best_od = None
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if best_od is None or d < best_od or (d == best_od and (rx, ry) < opp_target):
            best_od = d
            opp_target = (rx, ry)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Score the best resource we could aim to collect next from (nx, ny).
        # Prefer resources where we are not slower, and where the advantage is larger.
        local_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Advantage term: positive means we are closer/equal.
            adv = od - sd
            # If this is opponent's likely target, penalize if we are slower to it.
            block = 0
            if opp_target == (rx, ry):
                block = 3 if adv >= 0 else -5
            # Lower sd is always better; adv primarily drives contest.
            val = adv * 5 - sd + block
            if local_best is None or val > local_best[0] or (val == local_best[0] and (rx, ry) < local_best[1]):
                local_best = (val, (rx, ry))

        score = local_best[0]
        # Secondary: prefer moves that reduce our distance to the chosen best resource.
        rx, ry = local_best[1]
        score2 = man(nx, ny, rx, ry)
        key = (score, -score2)

        if best_score is None or key > best_score or (key == best_score and (dx, dy) < best_move):
            best_score = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]