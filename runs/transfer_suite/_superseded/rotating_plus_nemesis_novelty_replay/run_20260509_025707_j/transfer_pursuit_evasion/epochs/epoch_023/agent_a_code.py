def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if w < 1 or h < 1 or not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = str(observation.get("self_role") or "pursuer").lower()
    is_evader = role == "evader"

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    def cheb(x, y, a, b):
        dx = abs(x - a)
        dy = abs(y - b)
        return dx if dx > dy else dy

    obs_list = list(obstacles)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        dist_to_opp = cheb(nx, ny, ox, oy)

        # Obstacle avoidance: prefer moves that are farther from nearest obstacle.
        if obs_list:
            nearest = 10**9
            for ox2, oy2 in obs_list:
                d = abs(nx - ox2) + abs(ny - oy2)
                if d < nearest:
                    nearest = d
        else:
            nearest = 10**6

        # Tie-breaker: prefer center-ish to reduce zigzag trapping near edges.
        center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))

        if is_evader:
            # maximize survival: move to increase distance from pursuer
            score = (dist_to_opp, nearest, center_bias, -abs(dx) - abs(dy))
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        else:
            # pursue: minimize distance to opponent
            score = (-dist_to_opp, nearest, center_bias, -abs(dx) - abs(dy))
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]