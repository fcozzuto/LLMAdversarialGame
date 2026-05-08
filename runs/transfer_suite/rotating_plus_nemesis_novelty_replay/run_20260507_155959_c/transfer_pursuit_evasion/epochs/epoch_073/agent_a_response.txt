def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obs_list:
        try:
            x, y = p
            obs_set.add((int(x), int(y)))
        except Exception:
            pass

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = {(dx, dy): i for i, (dx, dy) in enumerate(moves)}

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def min_dist_to_obstacles(x, y):
        if not obs_set:
            return 99
        best = 99
        for ax, ay in obs_set:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist_op = abs(nx - ox) + abs(ny - oy)
        dist_obs = min_dist_to_obstacles(nx, ny)

        if is_evader:
            # Flee: maximize distance to pursuer; keep away from obstacles to avoid blocking.
            score = (dist_op * 1000) + (dist_obs * 10)
        else:
            # Pursue: minimize distance to pursuer; prefer squares away from obstacles to avoid corners/traps.
            score = (-dist_op * 1000) + (dist_obs * 2)

        if best_score is None or score > best_score or (score == best_score and order[(dx, dy)] < order[best]):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]