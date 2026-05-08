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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    obs_list = list(obstacles)

    def mind_obstacle_dist(x, y):
        md = 10**9
        for px, py in obs_list:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
                if md == 0:
                    break
        return md if md != 10**9 else 99

    # If obstacle is present, avoid tight areas; otherwise ignore.
    # Evader: maximize (dist to opponent + safety). Pursuer: minimize (dist to opponent - safety).
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        md = mind_obstacle_dist(nx, ny)
        safety = 0.0
        if obs_list:
            if md <= 0:
                safety = -10.0
            else:
                safety = min(4.0, md * 0.8)

        # slight bias to reduce oscillations: prefer direction aligned with current delta to opponent
        dir_bias = 0.0
        if dx != 0:
            dir_bias += 0.05 * (1 if dx == (1 if ox > sx else (-1 if ox < sx else 0)) else 0)
        if dy != 0:
            dir_bias += 0.05 * (1 if dy == (1 if oy > sy else (-1 if oy < sy else 0)) else 0)

        val = (dist + safety) if self_is_evader else (-(dist - safety) + dir_bias)
        if self_is_evader:
            better = best is None or val > best_val
        else:
            better = best is None or val > best_val

        if better:
            best = [dx, dy]
            best_val = val

    if best is None:
        return [0, 0]
    return best