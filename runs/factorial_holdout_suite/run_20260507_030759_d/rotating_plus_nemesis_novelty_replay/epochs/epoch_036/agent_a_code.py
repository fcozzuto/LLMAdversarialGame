def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate how good this move is by the best resource we could secure after moving.
        # Bonus for being closer to that resource than the opponent.
        # Small tie-break: prefer lower self distance to any resource (more progress).
        cur_best = -10**18
        min_self_any = 10**9
        for rx, ry in res:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            adv = od - sd
            # If we land adjacent, prioritize strongly (likely immediate collection depending on engine).
            adj_bonus = 2 if sd == 1 else (6 if sd == 0 else 0)
            block_bias = -0.2 * (manh(ox, oy, nx, ny))  # slightly discourage moving into opponent's approach
            score = adv * 10 + adj_bonus + block_bias
            if score > cur_best:
                cur_best = score
            if sd < min_self_any:
                min_self_any = sd

        # Progress/tiebreak
        total = cur_best - 0.05 * min_self_any
        if total > best_score:
            best_score = total
            best_move = [dx, dy]

    # If all invalid (shouldn't happen), stay.
    return best_move if best_move in ([d[0], d[1]] for d in deltas) else [0, 0]