def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.append((int(x), int(y)))
        except Exception:
            pass
    obs_set = set(obstacles)

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def mdist_to_obs(x, y):
        if not obstacles:
            return 99
        return min(abs(x - ax) + abs(y - ay) for ax, ay in obstacles)

    if is_evader:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = abs(nx - ox) + abs(ny - oy)
            d_corner = abs(tx - nx) + abs(ty - ny)
            score = (d_opp, -d_corner, mdist_to_obs(nx, ny))
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    else:
        # Pursuer: minimize distance to opponent.
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            # Prefer larger immediate reduction; tie-break by obstacle distance.
            reduction = (abs(sx - ox) + abs(sy - oy)) - d
            key = (-d, -reduction, -mdist_to_obs(nx, ny))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]