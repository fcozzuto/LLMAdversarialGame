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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def min_obs_dist(x, y):
        if not obstacles:
            return 10**6
        best = 10**6
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    def score_evader(nx, ny):
        # Prefer increasing distance, also avoid obstacles and discourage edge-sticking if opponent is aligned.
        d = abs(nx - ox) + abs(ny - oy)
        od = min_obs_dist(nx, ny)
        edge_bias = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            # edges can be dangerous; only slightly prefer them
            edge_bias = 0.5
        # Prefer moves that increase distance AND keep safe from obstacles.
        return d + 0.25 * (od - 1) + edge_bias

    def score_pursuer(nx, ny):
        # Prefer decreasing distance; also avoid obstacles and reduce "zigzag escape" by aiming for opponent's adjacent squares.
        d = abs(nx - ox) + abs(ny - oy)
        od = min_obs_dist(nx, ny)
        # Predict opponent tends to maximize distance; approximate by counting our move's ability to "corner" them:
        # If we're near an obstacle cluster, moving to reduce their options helps.
        options = 0
        for dx, dy in moves:
            ex, ey = ox + dx, oy + dy
            if valid(ex, ey):
                options += 1
        cornering = 1.5 * (options == 0) + 0.15 * options  # deterministic but harmless
        return -d + 0.06 * (od - 1) + cornering

    best_move = (0, 0)
    best_val = None

    # Deterministic tie-breaker order: smaller dx, then smaller dy.
    def tie_key(m):
        dx, dy = m
        return (dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = score_evader(nx, ny) if is_evader else score_pursuer(nx, ny)
        if best_val is None or val > best_val or (val == best_val and tie_key((dx, dy)) < tie_key(best_move)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]