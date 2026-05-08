def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    pursue = ("pursuer" in role) or ("pursur" in role)

    obst = set()
    for p in observation.get("obstacles", []):
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        adx, ady = nx - ox, ny - oy
        dist2 = adx * adx + ady * ady
        dist1 = abs(adx) + abs(ady)

        # For pursuer: minimize distance quickly; add slight bias to diagonal alignment.
        # For evader: maximize distance while moving away in both axes when possible.
        if pursue:
            align = 0.5 if (dx != 0 and dy != 0) else 0.0
            score = -(dist1 * 10 + dist2) + align
        else:
            away = (1 if ((nx > ox and sx <= ox) or (nx < ox and sx >= ox)) else 0) + (1 if ((ny > oy and sy <= oy) or (ny < oy and sy >= oy)) else 0)
            score = dist1 * 10 + dist2 + away * 0.5

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]