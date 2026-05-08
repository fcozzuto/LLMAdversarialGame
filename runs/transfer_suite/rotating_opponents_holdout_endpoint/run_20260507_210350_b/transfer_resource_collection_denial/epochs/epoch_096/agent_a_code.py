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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def king_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for (rx, ry) in resources:
        sd = king_dist(sx, sy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        # advantage = we arrive sooner; tie-break: closer self
        key = (od - sd, -sd, -king_dist(ox, oy, rx, ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    best_move = (0, 0)
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        d = king_dist(nx, ny, tx, ty)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    # If somehow no valid move (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]