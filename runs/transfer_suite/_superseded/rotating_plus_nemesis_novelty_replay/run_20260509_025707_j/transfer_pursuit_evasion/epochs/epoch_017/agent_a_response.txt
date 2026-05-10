def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w <= 0 or h <= 0 or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "pursuer").lower()
    i_am_evader = role == "evader"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def min_obs_dist(x, y):
        if not obstacles:
            return 99
        best = 99
        for (ox2, oy2) in obstacles:
            d = abs(x - ox2) + abs(y - oy2)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    best_move = [0, 0]
    best_score = -10**18 if not i_am_evader else -10**18
    # Evaluate: pursuer wants closer opponent and farther from obstacles; evader wants farther from opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_op = man(nx, ny, ox, oy)
        d_obs = min_obs_dist(nx, ny)
        # Bias toward cutting distance: larger weight on opponent; moderate on obstacle clearance.
        # Also discourage staying still when not needed.
        stay_pen = 0 if (dx != 0 or dy != 0) else 0.5
        score = (d_op if i_am_evader else -d_op) + (0.35 * d_obs if not i_am_evader else 0.15 * d_obs) - stay_pen
        if i_am_evader:
            if score > best_score:
                best_score, best_move = score, [dx, dy]
        else:
            if score > best_score:
                best_score, best_move = score, [dx, dy]

    return best_move