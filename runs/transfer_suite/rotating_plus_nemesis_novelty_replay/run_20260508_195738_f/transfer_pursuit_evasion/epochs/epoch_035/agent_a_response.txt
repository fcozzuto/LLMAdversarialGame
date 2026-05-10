def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    is_evader = str(observation.get("self_role", "")).lower() == "evader"
    # Precompute obstacle "repulsion" for scoring
    obs_list = list(obs)
    def obs_rep(x, y):
        if not obs_list:
            return 0.0
        best = 10**9
        for ex, ey in obs_list:
            d = abs(x - ex) + abs(y - ey)
            if d < best:
                best = d
        # Higher when closer; avoid hard constraints being handled by ok()
        return 1.0 / (1.0 + best)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy  # squared distance to opponent
        rep = obs_rep(nx, ny)

        if is_evader:
            # Maximize distance from pursuer, but don't hug obstacles/walls too tightly.
            score = (d2 * 1.0) + (rep * 4.0) + (-(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.02)
        else:
            # Pursuer: minimize distance to opponent; strongly avoid obstacles.
            # Prefer moves that reduce distance while not getting trapped near obstacles.
            score = (-d2 * 1.0) + (rep * -2.5)

        if best_score is None or (score > best_score):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]