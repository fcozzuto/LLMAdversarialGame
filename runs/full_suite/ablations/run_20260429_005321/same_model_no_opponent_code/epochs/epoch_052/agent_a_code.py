def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    try:
        sx, sy = int(sp[0]), int(sp[1])
        ox, oy = int(op[0]), int(op[1])
    except:
        sx, sy = 0, 0
        ox, oy = w - 1, h - 1

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    # Deterministic preference order for equal scores
    pref = {(0, 0): 0, (0, -1): 1, (-1, 0): 2, (1, 0): 3, (0, 1): 4, (-1, -1): 5, (1, -1): 6, (-1, 1): 7, (1, 1): 8}

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        if resources:
            # Go for nearest resource; break ties by favoring farthest from opponent
            dmin = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < dmin:
                    dmin = d
            do = abs(nx - ox) + abs(ny - oy)
            score = -2 * dmin + 0.1 * do
        else:
            # No resources known: move toward opponent if no obstacles block it, else stay
            d_to_opp = abs(nx - ox) + abs(ny - oy)
            score = -d_to_opp

        score -= 0.01 * pref.get((dx, dy), 99)
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best