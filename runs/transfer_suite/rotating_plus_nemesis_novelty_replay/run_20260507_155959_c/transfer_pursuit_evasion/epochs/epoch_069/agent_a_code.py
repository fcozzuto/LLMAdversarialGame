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
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def mdist_to_obs(x, y):
        if not obstacles:
            return 99
        best = 99
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    # Deterministic tie-break: fixed order moves, then smaller key components as written.
    best_move = [0, 0]
    if is_evader:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            safety = mdist_to_obs(nx, ny)
            # Primary: maximize distance from pursuer; secondary: maximize safety from obstacles.
            key = (-dist, -safety, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
    else:
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            safety = mdist_to_obs(nx, ny)
            # Primary: minimize distance to evader; secondary: maximize safety from obstacles.
            # Also lightly prefer moves that reduce absolute dx/dy changes deterministically.
            key = (dist, -safety, abs(dx), abs(dy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
    return best_move