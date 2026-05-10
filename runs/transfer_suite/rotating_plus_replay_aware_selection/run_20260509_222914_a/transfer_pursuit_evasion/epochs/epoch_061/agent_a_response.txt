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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def obstacle_pen(nx, ny):
        if (nx, ny) in obstacles:
            return 10**7
        pen = 0
        for bx, by in obstacles:
            m = abs(nx - bx) + abs(ny - by)
            if m == 0:
                pen += 10**6
            elif m == 1:
                pen += 2000
            elif m == 2:
                pen += 600
            elif m <= 4:
                pen += 120 // m
        return pen

    def edge_pen(nx, ny):
        # discourage getting stuck on borders when evading, lightly for pursuers
        return (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))

    best_val = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        d = man(nx, ny, ox, oy)
        pen = obstacle_pen(nx, ny)
        if is_pursuer:
            # minimize distance to opponent; avoid obstacles; keep moving
            val = d * 1000 + pen * 10 - (edge_pen(nx, ny) * 0.5) + (0 if (dx == 0 and dy == 0) else 0)
        else:
            # maximize distance; avoid obstacles; prefer central-ish moves slightly
            val = -d * 1000 + pen * 10 - (edge_pen(nx, ny) * -0.2) + (0 if (dx == 0 and dy == 0) else 0)

        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move