def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def adj_count(cell, S):
        x, y = cell
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in S:
                    c += 1
        return c

    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        cell = (nx, ny)

        score = 0
        if cell in opp_t:
            score += 14  # strong incentive to flip
        elif cell in unclaimed:
            score += 7
        elif cell in self_t:
            score += 3

        score += 0.6 * adj_count(cell, self_t)  # prefer extending frontier rooted in our territory

        # Center/space pressure: generally keep away from opponent unless capture/unclaimed.
        d_opp = dist2(nx, ny, ox, oy)
        score += 0.02 * (d_opp) if (cell in self_t or cell in unclaimed) else -0.02 * (d_opp)

        # Slight center attraction to avoid corner stagnation
        score += 0.01 * (-dist2(nx, ny, cx, cy))

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer moves that reduce manhattan to opponent, then lex order
            man_best = abs(sx + best_move[0] - ox) + abs(sy + best_move[1] - oy)
            man_new = abs(nx - ox) + abs(ny - oy)
            if man_new < man_best or (man_new == man_best and (dx, dy) < (best_move[0], best_move[1])):
                best_move = [dx, dy]

    dx, dy = int(best_move[0]), int(best_move[1])
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]