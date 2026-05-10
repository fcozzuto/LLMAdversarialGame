def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def blocked(x, y):
        return (x, y) in obstacles or not (0 <= x < w and 0 <= y < h)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not blocked(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Mobility (how many legal moves from the candidate), helps both roles deterministically.
    def mobility(x, y):
        c = 0
        for ddx, ddy in moves:
            tx, ty = x + ddx, y + ddy
            if not blocked(tx, ty):
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        dist = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)

        # Obstacle "tightness": count blocked neighbors around candidate
        tight = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if blocked(tx, ty):
                    tight += 1

        # Evader: maximize distance, mobility, and escape from tight areas.
        # Pursuer: minimize distance, prefer higher mobility to avoid being blocked, and avoid tight traps.
        if is_evader:
            score = (dist * 10) + (mob * 3) - (tight * 2)
            # If current is very close, prioritize moving away more aggressively.
            if dist <= 1:
                score += 50
        else:
            score = (-dist * 10) + (mob * 2) - (tight * 2)

        # Deterministic tie-breaker: lower dx, then lower dy.
        if best is None or score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best = (dx, dy)
            best_score = score

    return [int(best[0]), int(best[1])]