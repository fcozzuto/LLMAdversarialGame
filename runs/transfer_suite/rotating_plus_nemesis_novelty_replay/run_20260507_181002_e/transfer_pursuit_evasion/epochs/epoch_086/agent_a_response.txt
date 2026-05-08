def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "") or "")
    is_evader = ("evad" in role.lower())

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_block(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def dist2(x, y, x2, y2):
        dx = x - x2
        dy = y - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # If we are evading, prefer the corner maximizing distance from pursuer, but keep away from obstacles.
    target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d_to_op = dist2(nx, ny, ox, oy)
        d_to_corner = dist2(nx, ny, target_corner[0], target_corner[1])
        block_pen = adj_block(nx, ny)

        # pursuer: minimize distance; prefer less blocked squares; add slight preference to move closer to line to target corner
        # evader: maximize distance; prefer more open squares; add slight preference to reach preferred corner
        if is_evader:
            val = (d_to_op * 3) + (d_to_corner * 0.2) - (block_pen * 2.0)
        else:
            val = (-d_to_op * 3) - (block_pen * 2.0) + (d_to_corner * -0.05)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]