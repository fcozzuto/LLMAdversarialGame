def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))
    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)
    capr = int(observation.get("capture_radius") or 0)

    obs_list = list(blocked)

    def cheb(x, y):
        ax = abs(x - ox)
        ay = abs(y - oy)
        return ax if ax > ay else ay

    def manh_to_nearest_obstacle(x, y):
        if not obs_list:
            return 99
        best = 99
        for bx, by in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        d = cheb(nx, ny)
        obstacle_clear = manh_to_nearest_obstacle(nx, ny)

        # Primary objective: capture if pursuer, avoid capture if evader
        if capr == 0:
            capture_term = (0 if d == 0 else 1)
        else:
            capture_term = (0 if d <= capr else 1)

        if not is_evader:
            # maximize: closer to opponent; strongly prefer immediate capture
            score = (100000 if capture_term == 0 else 0) + (1000 - d * 10) + obstacle_clear
        else:
            # maximize: farther from opponent; strongly penalize getting within capture radius
            score = (0 if capture_term == 0 else 100000) + (d * 10) + obstacle_clear

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # Fallback: deterministic step along best axis without considering obstacles
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        if is_evader:
            dx, dy = -dx, -dy
        best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]