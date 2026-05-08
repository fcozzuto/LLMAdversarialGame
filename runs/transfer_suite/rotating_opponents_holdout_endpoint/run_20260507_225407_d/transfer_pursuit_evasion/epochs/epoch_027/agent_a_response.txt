def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    turn = int(observation.get("turn_index", 0) or 0)

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

    def man(ax, ay, bx, by):
        return abs(bx - ax) + abs(by - ay)

    def obs_pen(x, y):
        pen = 0
        for (px, py) in obstacles:
            d = max(0, man(x, y, px, py))
            if d == 0:
                return 10**6
            if d == 1:
                pen += 3
            elif d == 2:
                pen += 1
        return pen

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    if is_pursuer:
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, ox, oy)
            wall = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
            v = (-d) + 0.15 * wall - 1.2 * obs_pen(nx, ny)
            if v > best_val:
                best_val, best_move = v, [dx, dy]
    else:
        # Evader: alternate corner choice to disrupt zigzag, still obstacle-aware.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        pref = corners[turn % 4]
        # Prefer farthest from pursuer; in tie, prefer moves that head toward pref corner.
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, ox, oy)
            wall = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
            toward = man(nx, ny, pref[0], pref[1])
            v = d + 0.25 * wall - 0.6 * toward - 1.2 * obs_pen(nx, ny)
            if v > best_val:
                best_val, best_move = v, [dx, dy]
    return best_move