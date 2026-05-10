def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("flee" in role) or ("escape" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def min_obs_dist(x, y):
        if not obstacles:
            return 10**6
        best = 10**6
        for px, py in obstacles:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        return best

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def toward_target_move():
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        cx, cy = sx + dx, sy + dy
        if in_bounds(cx, cy) and (cx, cy) not in obs:
            return [dx, dy]
        return None

    pref = toward_target_move()
    if pref is not None and observation.get("turn_index", 0) % 2 == 0:
        return pref

    best = None
    best_move = [0, 0]
    ti = observation.get("turn_index", 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        d = cheb(nx, ny)
        md = min_obs_dist(nx, ny)
        # Deterministic tie-break by (dx, dy) rotated with turn index
        rot = (dx + 2 * (dy + 1) + ti) % 7

        if is_evader:
            score = (d, md, -rot)
            if best is None or score > best:
                best = score
                best_move = [dx, dy]
        else:
            score = (-d, md, -rot)
            if best is None or score > best:
                best = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]