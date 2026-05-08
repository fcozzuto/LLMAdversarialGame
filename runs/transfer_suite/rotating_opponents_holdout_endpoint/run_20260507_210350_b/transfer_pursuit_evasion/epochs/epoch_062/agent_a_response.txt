def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    self_is_evader = ("evader" in role_self) or ("runner" in role_self) or ("evasion" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_penalty(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    pen += 2
        return pen

    def score_evader(x, y):
        target_corner = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
        base = manh(x, y, target_corner[0], target_corner[1]) + manh(x, y, corners[0][0], corners[0][1])
        away = manh(x, y, ox, oy)
        return away * 4 + base - obstacle_penalty(x, y)

    def score_pursuer(x, y):
        d = manh(x, y, ox, oy)
        return -d * 5 - obstacle_penalty(x, y)

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = score_evader(nx, ny) if self_is_evader else score_pursuer(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move