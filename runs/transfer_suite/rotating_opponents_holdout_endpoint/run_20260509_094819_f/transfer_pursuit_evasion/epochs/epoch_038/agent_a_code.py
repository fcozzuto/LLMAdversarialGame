def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    role = (str(observation.get("self_role", "")) + " " + str(observation.get("environment_name", ""))).lower()
    evader = ("evad" in role) or ("escape" in role) or ("runner" in role) or ("evasion" in role) or ("pursuer" not in role and "evad" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def free_neighbors(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if ok(nx, ny):
                    c += 1
        return c

    # Chasing: greedily reduce distance, but avoid getting trapped near obstacles (wall-running).
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dsq = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        md = abs(nx - ox) + abs(ny - oy)
        slack = free_neighbors(nx, ny)  # higher is safer
        corner = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)

        if evader:
            # Evade: maximize distance, also move toward lower local mobility to hinder pursuer.
            score = dsq + 0.35 * md - 0.25 * slack - (0.05 if corner else 0.0)
        else:
            # Pursue: minimize distance, penalize low mobility, and slightly prefer breaking into open space.
            score = -dsq - 0.25 * md + 0.22 * slack + (0.04 if corner else 0.0)

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]