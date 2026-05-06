def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def to_xy(p, default):
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
            elif isinstance(p, dict):
                x = p.get("x", p.get("X", p.get("col", p.get("cx", default[0]))))
                y = p.get("y", p.get("Y", p.get("row", p.get("cy", default[1]))))
                x, y = int(x), int(y)
            else:
                return default
            if 0 <= x < w and 0 <= y < h:
                return (x, y)
        except Exception:
            pass
        return default

    sp = to_xy(observation.get("self_position", None), (0, 0))
    op = to_xy(observation.get("opponent_position", None), (w - 1, h - 1))
    sx, sy = sp
    ox, oy = op

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        p = to_xy(o, None)
        if p is not None:
            obstacles.add(p)

    resources = []
    for r in observation.get("resources", []) or []:
        p = to_xy(r, None)
        if p is not None and p not in obstacles:
            resources.append(p)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Steal-oriented: pick move that maximizes advantage (opponent closer -> bad; our closer -> good),
    # with tie-breakers for safety (avoid obstacles) and progress (closer to chosen resource).
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # For this candidate position, evaluate the best resource to pursue.
        local_best = None
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # advantage: positive when we are closer than opponent
            adv = od - sd
            # small bias toward making quicker progress to avoid dithering
            prog = -0.08 * sd
            # slight bias to prefer staying away from opponent when equally good
            opp_rel = -0.02 * (abs(nx - ox) + abs(ny - oy))
            score = adv + prog + opp_rel
            key = (score, -sd, -adv)  # deterministic lexicographic
            if local_best is None or key > local_best[0]:
                local_best = (key, rx, ry)

        if local_best is None:
            continue
        score_key = local_best[0]
        if best_score is None or score_key > best_score:
            best_score = score_key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]