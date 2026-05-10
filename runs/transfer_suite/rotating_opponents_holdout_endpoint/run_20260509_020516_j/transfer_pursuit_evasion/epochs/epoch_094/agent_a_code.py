def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    if not (0 <= sx < w and 0 <= sy < h) or (sx, sy) in obstacles:
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))
        if (sx, sy) in obstacles:
            for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    sx, sy = nx, ny
                    break

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x, y, a, b):
        return abs(x - a) + abs(y - b)
    def clamp_score(x):
        return x if x >= -10**9 else -10**9

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        d = man(nx, ny, ox, oy)
        dist_term = d if is_evader else -d

        # Wall/obstacle proximity pressure: avoid being adjacent to obstacles as evader,
        # but approach them as pursuer to constrain evader options.
        prox = 0
        for ax, ay in obstacles:
            md = man(nx, ny, ax, ay)
            if md == 0:
                prox -= 999
            else:
                prox += (1.5 / md)
        obstacle_term = (prox if is_evader else -prox)

        # Keep away from board edges when evading; prefer edges when pursuing (simple constraint).
        edge_dist = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        edge_term = (edge_dist if is_evader else -edge_dist)

        # Deterministic tie-breaking: small bias towards reducing (or increasing) both coords together.
        diag_bias = -(abs((nx - ox)) + abs((ny - oy))) if not is_evader else (abs((nx - ox)) + abs((ny - oy)))

        score = dist_term + 0.9 * obstacle_term + 0.35 * edge_term + 0.01 * diag_bias
        score = clamp_score(score)

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]