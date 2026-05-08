def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursue" in self_role) or (("pursuit" in self_role) and ("evasion" not in self_role))
    is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("escape" in self_role)
    if not is_pursuer and not is_evader:
        is_pursuer = ("pursuer" in opp_role)
        is_evader = not is_pursuer

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(bx - ax) + abs(by - ay)

    def wall_prox(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_m = [0, 0]

    if is_pursuer:
        # Greedy chase with obstacle avoidance; tie-break to keep us away from getting "pinned" near walls.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist(nx, ny, ox, oy)
            score = (d, -wall_prox(nx, ny), abs(ox - nx) + abs(oy - ny))  # deterministic
            if best is None or score < best:
                best, best_m = score, [dx, dy]
        return best_m
    else:
        # Run away: maximize distance, and prefer moves that keep us away from obstacles.
        def obstacle_penalty(x, y):
            pen = 0
            for tx, ty in ((x+1,y),(x-1,y),(x,y+1),(x,y-1),(x+1,y+1),(x-1,y-1),(x+1,y-1),(x-1,y+1)):
                if inside(tx, ty) and (tx, ty) in obstacles:
                    pen += 1
            return pen

        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist(nx, ny, ox, oy)
            score = (-d, obstacle_penalty(nx, ny), -wall_prox(nx, ny))
            if best is None or score < best:
                best, best_m = score, [dx, dy]
        return best_m