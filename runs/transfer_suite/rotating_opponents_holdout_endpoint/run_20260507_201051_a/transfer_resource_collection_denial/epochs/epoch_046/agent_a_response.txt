def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) + abs(dy)

    # Pick a target resource where we have the best distance advantage.
    best_target = resources[0]
    best_tscore = -10**18
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Strongly prefer resources where we are closer than opponent.
        tscore = (opd - myd) * 100 - myd
        if tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry)

    rx, ry = best_target

    # Evaluate our next step: maximize our advantage for that target, avoid obstacles/out of bounds.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = dist(nx, ny, rx, ry)
        opd2 = dist(ox, oy, rx, ry)  # opponent unchanged this turn (turn-based)
        val = (opd2 - myd2) * 100 - myd2
        # Extra: if we can pick up now, prioritize heavily.
        if nx == rx and ny == ry:
            val += 10**7
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all moves were invalid (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]