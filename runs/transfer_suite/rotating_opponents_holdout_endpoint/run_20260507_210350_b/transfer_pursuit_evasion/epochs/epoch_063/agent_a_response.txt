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
    self_is_evader = ("evader" in role_self) or ("runner" in role_self) or ("evasion" in role_self) or ("escape" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10_000
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    pen += 3
        return pen

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        p = obs_pen(nx, ny)
        if self_is_evader:
            target_corner = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
            # prefer increasing distance to pursuer; also bias toward farthest corner
            d = manh(nx, ny, ox, oy)
            v = (d * 5) + (manh(nx, ny, target_corner[0], target_corner[1]) * 2) - p
        else:
            # pursuer: reduce distance to evader while avoiding obstacles and staying near center slightly
            d = manh(nx, ny, ox, oy)
            center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            v = (-d * 6) + (center_bias * 0.5) - p

        if best is None:
            best, bestv = [dx, dy], v
        else:
            if self_is_evader:
                if v > bestv:
                    best, bestv = [dx, dy], v
            else:
                if v > bestv:
                    best, bestv = [dx, dy], v

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]