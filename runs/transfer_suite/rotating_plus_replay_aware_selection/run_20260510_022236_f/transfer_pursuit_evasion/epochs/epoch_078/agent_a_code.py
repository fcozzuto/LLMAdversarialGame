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
    # Prefer deterministic tie-breaking: fixed move order already.
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)

        # Local mobility: count free neighbors around candidate
        free_nb = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if not blocked(tx, ty):
                free_nb += 1

        # Proximity to obstacles: higher if surrounded -> worse
        near_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if (tx, ty) in obstacles:
                    near_obs += 1
                elif not (0 <= tx < w and 0 <= ty < h):
                    near_obs += 1

        # Small directional bias to avoid oscillation: prefer moving away/toward based on role
        dir_bias = 0
        if is_evader:
            dir_bias = (dx * (nx - ox) + dy * (ny - oy))
        else:
            dir_bias = -(dx * (nx - ox) + dy * (ny - oy))

        # Score
        if is_evader:
            # Maximize distance, mobility, and escape from obstacles
            score = (dist * 3.0) + (free_nb * 0.8) - (near_obs * 0.6) + (dir_bias * 0.01)
            # If corner/trap-like (low free_nb), heavily penalize
            if free_nb <= 3:
                score -= 2.5
        else:
            # Minimize distance, but avoid stepping into tight pockets
            score = (-dist * 3.0) + (free_nb * 0.4) - (near_obs * 0.4) + (dir_bias * 0.01)
            if free_nb <= 3:
                score -= 1.5

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]