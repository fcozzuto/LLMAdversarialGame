def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    manh = lambda x1, y1, x2, y2: abs(x1 - x2) + abs(y1 - y2)
    cheb = lambda x1, y1, x2, y2: max(abs(x1 - x2), abs(y1 - y2))

    # Predict opponent target: nearest resource by opponent (nearest_resource archetype)
    scored_res = []
    for rx, ry in resources:
        scored_res.append((manh(ox, oy, rx, ry), rx, ry))
    scored_res.sort(key=lambda t: (t[0], t[1], t[2]))
    candidate_targets = scored_res[:2]  # second chance if nearest is too "expensive" to contest

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Contention heuristic against likely opponent targets (not global scan)
        best_for_move = None
        for oppd, rx, ry in candidate_targets:
            myd = manh(nx, ny, rx, ry)
            # Prefer reaching at least as fast (adv>=0), then faster lead, then diagonal/chebyshev progress
            adv = oppd - myd
            diag_prog = -cheb(nx, ny, rx, ry)
            tie_res_push = -(abs(rx - ox) + abs(ry - oy))  # slightly disrupt opponent's geometry
            # Also discourage moves that leave us far while opponent is close
            key = (adv >= 0, adv, diag_prog, tie_res_push)
            if best_for_move is None or key > best_for_move:
                best_for_move = key

        # Anti-stall: if adv-fairness ties, don't keep still unless equally good
        stall_pen = 1 if (dx == 0 and dy == 0) else 0
        overall = (best_for_move, -stall_pen, -manh(nx, ny, ox, oy), dx, dy)
        if best_key is None or overall > best_key:
            best_key = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]