def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("catch" in role) or ("pred" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]]

    def min_obst_dist(x, y):
        if not obstacles:
            return 7
        md = 99
        for (oxb, oyb) in obstacles:
            d = abs(x - oxb) + abs(y - oyb)
            if d < md:
                md = d
                if md <= 0:
                    break
        return md if md != 99 else 7

    cur_dist = abs(sx - ox) + abs(sy - oy)
    if pursuer:
        target = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best_move = (0, 0)
    best_score = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        d_ob = min_obst_dist(nx, ny)
        toward_corner = -(abs(target[0] - nx) + abs(target[1] - ny)) if pursuer else (abs(target[0] - nx) + abs(target[1] - ny))
        # Primary: pursuit/evade distance; Secondary: obstacle clearance; Tertiary: corner pressure
        score = (-dist if pursuer else dist) + (0.35 * d_ob) + (0.08 * toward_corner)

        key = (round(score, 6), -dx, -dy)  # deterministic tie-break
        if best_score is None or score > best_score or (score == best_score and key > best_key):
            best_score = score
            best_move = (dx, dy)
            best_key = key

    if best_move == (0, 0):
        # Fallback: step that changes your distance the most while not hitting obstacles
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            nd = abs(nx - ox) + abs(ny - oy)
            delta = nd - cur_dist
            better = (delta < 0) if pursuer else (delta > 0)
            mag = abs(delta)
            if best_d is None or (better, mag, -dx, -dy) > best_d:
                best_d = (better, mag, -dx, -dy)
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]