def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = observation.get("self_role", "")
    role_pursuer = (self_role == "pursuer") or ("pursuer" in str(self_role).lower())

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny)
        sumd = abs(nx - ox) + abs(ny - oy)
        diag = 1 if (dx != 0 and dy != 0) else 0
        toward_x = 0 if (nx == ox) else (1 if (nx > ox) else -1)
        toward_y = 0 if (ny == oy) else (1 if (ny > oy) else -1)
        toward = (0 if (toward_x == 0 and toward_y == 0) else 1)

        # Center bias: evader prefers staying away from corners; pursuer doesn't care much.
        center_dist = abs(nx - cx) + abs(ny - cy)

        if role_pursuer:
            # minimize distance; tie-break by stronger progress and diagonal, avoid staying.
            key = (d, sumd, -diag, 0 if (dx == 0 and dy == 0) else -1, -center_dist)
        else:
            # maximize distance; tie-break by moving and pushing toward center.
            key = (-d, -sumd, -(diag), 0 if (dx == 0 and dy == 0) else -1, -center_dist)

        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

        if d == 0 and role_pursuer:
            return best_move

    return best_move