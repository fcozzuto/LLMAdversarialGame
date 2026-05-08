def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr) or (("pursuer" not in sr) and ("evader" in orr))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_near_score(x, y):
        if not obstacles:
            return 0
        md = 10**9
        for px, py in obstacles:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
                if md == 0:
                    break
        return -md  # closer -> worse

    # Prefer staying within bounds; engine keeps in place if invalid, so avoid invalid.
    best = None
    best_val = None
    # Tie-break order: smallest dx,dy lexicographically for determinism.
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        cheb = max(abs(nx - ox), abs(ny - oy))
        man = abs(nx - ox) + abs(ny - oy)

        # Evader: maximize distance; Pursuer: minimize distance.
        obs_pen = obstacle_near_score(nx, ny)
        boundary_pen = -(min(nx, w - 1 - nx) + min(ny, h - 1 - ny)) * 0.02  # mild anti-corner for evader

        if self_is_evader:
            val = cheb * 2.0 + man * 0.2 + obs_pen * 1.0 + boundary_pen * 1.0
        else:
            val = -cheb * 2.0 - man * 0.2 + obs_pen * 1.0 + boundary_pen * -1.0

        if best is None or (val > best_val if self_is_evader else val > best_val):
            best = [dx, dy]
            best_val = val

    # If all moves invalid (rare), stay.
    if best is None:
        return [0, 0]
    return best