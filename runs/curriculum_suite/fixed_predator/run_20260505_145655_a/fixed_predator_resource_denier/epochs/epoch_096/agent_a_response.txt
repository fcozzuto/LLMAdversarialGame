def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Evaluate next move by contesting up to 3 most "relevant" resources:
    # relevance = opponent closeness minus our closeness (we deny when they are likely to arrive first).
    top = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        rel = od - sd
        top.append((rel, rx, ry))
    top.sort(key=lambda t: (-(t[0]), man(sx, sy, t[1], t[2])))
    top = top[:3]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_score = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        score = 0
        for rel, rx, ry in top:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Denial pressure: if opponent is closer, we get big bonus by reducing sd.
            # If we're closer, we get bonus for continuing the race while not letting opponent too close.
            score += (od - sd) * 12 - sd * 1.2
            if sd <= od:
                score += 6
            else:
                score -= 4
            # Small tie-break toward resources that are generally closer to us.
            score -= 0.001 * (rx + ry)
        # Tie-break deterministically by preferring moves with smaller distance to best resource from current
        # (keeps behavior stable run-to-run).
        _, bx, by = top[0]
        score -= 0.01 * man(nx, ny, bx, by)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]