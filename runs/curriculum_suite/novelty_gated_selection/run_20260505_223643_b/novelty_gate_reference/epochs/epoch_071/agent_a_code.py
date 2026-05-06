def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    edge = lambda x, y: 1 if x in (0, w - 1) or y in (0, h - 1) else 0

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate this move by the best resource we can contest.
        move_best = None
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # Prefer resources where we are closer than opponent, especially those with small absolute distance.
            # Also slightly prefer moving toward board edges (useful for cornering) to create deterministic pressure.
            rel = (opp_d - our_d)
            dist_term = -our_d
            contest_term = 2.5 * rel
            edge_term = -0.3 * edge(nx, ny)
            block_term = -0.1 * (1 if (nx + (rx - nx) // 2, ny + (ry - ny) // 2) in obstacles else 0)

            score = contest_term + dist_term + edge_term + block_term
            if move_best is None or score > move_best:
                move_best = score

        # Tie-break deterministically by lexicographic (dx,dy) after score.
        total = move_best if move_best is not None else -10**9
        cand = (total, -edge(nx, ny), -man(nx, ny, ox, oy), dx, dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = [dx, dy]

    return best_move