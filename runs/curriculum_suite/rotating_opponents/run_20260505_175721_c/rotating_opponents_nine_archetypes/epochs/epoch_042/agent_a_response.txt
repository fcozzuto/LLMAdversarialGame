def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = None

    # Resource-denial heuristic: move to reduce opponent advantage on resources they are closest to.
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        opp_closer_best = 0
        my_catch_best = 0
        for tx, ty in resources:
            myd = man(nx, ny, tx, ty)
            opd = man(ox, oy, tx, ty)

            rel = myd - opd  # negative means I'm closer than opponent
            # If opponent is closer now, prioritize moving so I become not-too-far behind.
            if opd < myd:
                opp_closer_best = max(opp_closer_best, opd - myd)  # larger = I reduced being behind
            # If I can match/overtake, prioritize bringing down actual distance.
            if rel <= 0:
                my_catch_best = max(my_catch_best, 20 - myd)  # closer resource => higher

        # Combine: prefer immediate catch; otherwise reduce opponent's lead.
        score = (my_catch_best * 1000) + opp_closer_best
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]