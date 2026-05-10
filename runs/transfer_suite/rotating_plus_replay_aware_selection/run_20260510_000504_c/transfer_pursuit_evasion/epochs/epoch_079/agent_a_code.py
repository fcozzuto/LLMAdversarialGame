def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best_dx, best_dy = 0, 0
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        dist = d2(nx, ny)

        # Small obstacle-avoidance preference even if staying is forced by engine.
        stay_pen = 0 if (nx != sx or ny != sy) else 0.1
        if is_evader:
            val = dist - stay_pen
        else:
            val = -dist - stay_pen

        if best is None:
            best = val
            best_dx, best_dy = dx, dy
        else:
            if val > best:
                best = val
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]