def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def quadrant_bonus(tx, ty):
        # Bias towards pushing into area closer to us than opponent in both axes
        usx = 1 if tx >= sx else -1
        usy = 1 if ty >= sy else -1
        osx = 1 if tx >= ox else -1
        osy = 1 if ty >= oy else -1
        return (usx == osx) + (usy == osy)

    # Prefer resources where we are closer; otherwise choose ones that minimize the lead gap.
    best = None
    best_val = -10**18
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        lead = od - sd
        # Encourage taking over when lead is possible; otherwise reduce total competition distance.
        if sd <= od:
            val = 3 * lead + quadrant_bonus(rx, ry) * 0.5 - 0.01 * sd
        else:
            val = 1.5 * lead - 0.01 * (sd + od) - 0.05 * quadrant_bonus(rx, ry)
        if val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Avoid stepping into obstacles; choose move that improves our distance and keeps opponent from getting advantage.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = md(nx, ny, rx, ry)
        od2 = md(ox, oy, rx, ry)
        score = (od2 - sd2) * 2.0 - 0.01 * sd2
        # Small tie-break to keep motion consistent: prefer forward-ish towards target.
        score += -0.001 * (abs(nx - rx) + abs(ny - ry))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]