def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    obs_list = list(obstacles)

    def obstacle_score(x, y):
        if (x, y) in obstacles:
            return 10**7
        if not obs_list:
            return 0
        best = 10**9
        near = 0
        for bx, by in obs_list:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
            if d == 0:
                near += 1
        if best == 0:
            return 10**7
        return (600 if best == 1 else 160 if best == 2 else 70 if best <= 3 else 0)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_pursuer:
        target = None
        pref = 0
    else:
        target = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
        pref = 1

    best_val = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        d2 = man(nx, ny, ox, oy)
        o_pen = obstacle_score(nx, ny)
        if o_pen >= 10**6:
            continue
        if is_pursuer:
            # chase with slight side-bias to avoid straight-line trapping by obstacles
            val = d2 * 1000 + o_pen
            # encourage moving toward the same quadrant as opponent
            val += (0 if (dx == 0 and dy == 0) else (0 if (nx - ox) * (sx - ox) <= 0 else 20))
        else:
            # evade: maximize distance, also bias toward farthest corner
            val = -d2 * 1000 + o_pen
            if pref:
                val += man(nx, ny, target[0], target[1]) * 2
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]