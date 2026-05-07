def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obst = observation.get("obstacles") or []
    obstacles = set()
    for p in obst:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not inb(sx, sy):
        return [0, 0]
    if not resources:
        return [0, 0]

    res_set = set((r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2)
    resources_list = [(rx, ry) for (rx, ry) in res_set if inb(rx, ry)]
    if not resources_list:
        return [0, 0]

    best_score = -(10**18)
    best_move = (0, 0)

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        our_on_resource = 1.0 if (nsx, nsy) in res_set else 0.0

        # Evaluate by best resource we can reach quickly vs opponent.
        # Prefer moves that secure a resource first.
        min_our = 10**9
        min_opp_for_ourmin = 10**9
        for rx, ry in resources_list:
            od = cd(nsx, nsy, rx, ry)
            if od < min_our:
                min_our = od
                min_opp_for_ourmin = cd(ox, oy, rx, ry)
            elif od == min_our:
                oppd = cd(ox, oy, rx, ry)
                if oppd < min_opp_for_ourmin:
                    min_opp_for_ourmin = oppd

        # Higher is better: prioritize smaller our distance; penalize if opponent can beat us.
        # Also slightly reward moving closer even if contested.
        contest_gap = min_opp_for_ourmin - min_our  # positive means we are closer
        score = (our_on_resource * 1000.0) + (contest_gap * 10.0) - (min_our * 1.2) - (min_opp_for_ourmin * 0.2)

        # Deterministic tie-break: consistent ordering based on move.
        if score > best_score:
            best_score = score
            best_move = (mdx, mdy)
        elif score == best_score:
            if (mdx, mdy) < best_move:
                best_move = (mdx, mdy)

    return [best_move[0], best_move[1]]