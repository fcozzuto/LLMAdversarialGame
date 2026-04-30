def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    # If no resources reported, just move away from opponent while staying safe-ish
    if not resources:
        best = None
        best_d = -1
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, ox, oy)
            if d > best_d:
                best_d = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # One-move "race" heuristic: maximize advantage for the best contested resource.
    best_move = (0, 0)
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Advantage = (opponent distance) - (my distance) to the same resource
        # Prefer higher advantage; tie-break by smaller my distance to that advantaged resource.
        best_adv = None
        best_my_dist = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            if best_adv is None or adv > best_adv or (adv == best_adv and my_d < best_my_dist):
                best_adv = adv
                best_my_dist = my_d

        # Secondary tie-break: also avoid approaching the nearest obstacle too much
        nearest_obs = None
        for (bx, by) in obstacles:
            d = cheb(nx, ny, bx, by)
            if nearest_obs is None or d < nearest_obs:
                nearest_obs = d
        nearest_obs = 0 if nearest_obs is None else nearest_obs

        key = (best_adv, nearest_obs, -best_my_dist, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]