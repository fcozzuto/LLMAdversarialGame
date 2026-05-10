def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)

        min_obs = 99
        sum_obs = 0
        for bx, by in obstacles:
            d = cheb(nx, ny, bx, by)
            if d < min_obs: min_obs = d
            sum_obs += d
            if d == 0:
                min_obs = 0
                break

        if min_obs == 0:
            continue

        if evader:
            # maximize distance from pursuer, keep away from obstacles
            primary = d_opp
            secondary = min_obs
            tertiary = -sum_obs
            score = (primary, secondary, tertiary)
        else:
            # minimize distance to evader, keep away from obstacles
            primary = -d_opp
            secondary = min_obs
            tertiary = -sum_obs
            score = (primary, secondary, tertiary)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move