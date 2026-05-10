def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def valid(x, y):
        return inb(x, y) and (x, y) not in blocked

    def options(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        center_bias = -0.0008 * dist2(nx, ny, int(cx), int(cy))
        my_opts = options(nx, ny)

        if is_evader:
            # Run away, but avoid trapping yourself near obstacles.
            val = d + 0.02 * my_opts + center_bias
        else:
            # Chase: reduce distance; keep enough mobility to avoid local traps.
            val = -d + 0.02 * my_opts + center_bias

        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if is_evader:
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]
            else:
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]

    return best_move