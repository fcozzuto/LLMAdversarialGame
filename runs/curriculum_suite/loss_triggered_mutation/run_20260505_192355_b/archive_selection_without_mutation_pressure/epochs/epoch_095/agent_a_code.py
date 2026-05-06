def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_value(px, py):
        best = None
        for rx, ry in resources:
            md = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer high advantage, then shorter own distance, then farther from opponent to reduce contest.
            val = (od - md) * 100 - md + (od < md) * 5
            # If tie on val, prefer lower md.
            cand = (val, -md)
            if best is None or cand > best[0]:
                best = (cand, md)
        return best[0][0], best[0][1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            score = -10**18
        else:
            v, neg_md = best_value(nx, ny)
            # Small tie-break: reduce risk of giving opponent access by moving generally toward resources
            # closer than opponent by at least 1.
            my_to_best = -neg_md
            opp_to_best = my_to_best + max(0, (v // 100))
            score = v * 10 + (opp_to_best - my_to_best) * 2 - my_to_best * 0.05
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]