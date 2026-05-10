def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid_moves.append((dx, dy))
    if not valid_moves:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (man(ox, oy, c[0], c[1]) - 0.05 * man(sx, sy, c[0], c[1])))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res = [(int(r[0]), int(r[1])) for r in resources]

    # If opponent is closer to a resource, we bias against it; otherwise we go for it.
    alpha = 1.15
    gamma = 0.02  # slight tie-break toward shorter own distance
    best_dxdy = None
    best_val = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        val = -1e9
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Higher is better:
            #  - immediate progress (lower sd)
            #  - resource denial (make sd < od attractive)
            #  - discourage moving away from any resource too much
            score = alpha * (od - sd) - gamma * sd
            if score > val:
                val = score
        if best_val is None or val > best_val:
            best_val = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]