def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Resource-denial counter: pick a resource we can reach no later than the opponent, otherwise the best remaining advantage.
    best = None
    best_gap = -10**9
    best_sd = 10**9
    best_cell = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        gap = od - sd
        penalty = 0
        if sd > od:
            penalty = 3  # strongly prefer resources where we are not slower
        val = gap - penalty
        if (val > best_gap) or (val == best_gap and (sd < best_sd or (sd == best_sd and (rx, ry) < (best_cell[0], best_cell[1] if best_cell else (10**9, 10**9))))):
            best_gap = val
            best_sd = sd
            best_cell = (rx, ry)

    tx, ty = best_cell

    # Choose a move that reduces our distance to the chosen target and maintains/creates advantage versus opponent.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, tx, ty)
        # Maintain advantage; reward getting closer to target; discourage moving away.
        score = (od2 - sd2) * 10 - sd2
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]