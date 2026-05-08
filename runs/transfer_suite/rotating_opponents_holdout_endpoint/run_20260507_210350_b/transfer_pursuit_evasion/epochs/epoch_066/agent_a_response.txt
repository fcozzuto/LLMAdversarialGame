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
    is_evader = ("evader" in role_self) or ("runner" in role_self) or ("evasion" in role_self) or ("escape" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    k = int(observation.get("turn_index", 0) or 0) % 4
    target_corner = corners[k]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy  # Chebyshev

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10_000_000
        pen = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    pen += 4
        return pen

    start_d = dist(sx, sy, ox, oy)
    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        pen = obs_pen(nx, ny)
        d_to_opp = dist(nx, ny, ox, oy)

        tx, ty = target_corner
        d_to_corner = dist(nx, ny, tx, ty)
        corner_val = -d_to_corner if is_evader else -d_to_corner

        # pursuer: minimize distance; evader: maximize distance
        if is_evader:
            val = (d_to_opp - start_d * 0.02) + 0.15 * corner_val - pen
        else:
            val = (-d_to_opp + start_d * 0.02) - 0.1 * corner_val - pen

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move