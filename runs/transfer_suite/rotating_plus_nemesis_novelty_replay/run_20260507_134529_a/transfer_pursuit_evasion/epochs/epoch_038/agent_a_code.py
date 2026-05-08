def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    w = int(w) if w is not None else 8
    h = int(h) if h is not None else 8

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2 and p[0] is not None and p[1] is not None:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    evade = ("evader" in role) or (("evader" in orole) and ("pursuer" not in role))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = d2 if evade else -d2

        if best is None:
            best = [dx, dy]
            best_score = score
        else:
            if score > best_score:
                best = [dx, dy]
                best_score = score
            elif score == best_score:
                if dx != best[0]:
                    if dx > best[0]:
                        best = [dx, dy]
                else:
                    if dy > best[1]:
                        best = [dx, dy]

    if best is None:
        return [0, 0]
    return best