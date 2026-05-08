def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is None:
            continue
        try:
            x, y = int(p[0]), int(p[1])
            obs.add((x, y))
        except Exception:
            pass

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursur" in role) or (role == "pursuer")

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manhattan(x, y):
        return abs(x - ox) + abs(y - oy)

    best = None
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = manhattan(nx, ny)
        # pursuer: minimize distance; evader: maximize distance. Tie-break to move toward nearest corner for determinism.
        corner_bias = (nx <= w // 2) ^ (ny <= h // 2)
        score = d if not pursuer else -d
        score = score * 10000 + (-1 if corner_bias else 0)
        if best_score is None or (score < best_score if pursuer else score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]