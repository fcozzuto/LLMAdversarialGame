def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = "evader" in role

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in ob

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def score(x, y):
        d_to_op = man(x, y, ox, oy)
        cx, cy = (max(corners, key=lambda c: man(c[0], c[1], ox, oy)) if evader
                  else min(corners, key=lambda c: man(c[0], c[1], ox, oy)))
        d_to_corner = man(x, y, cx, cy)
        # If evader: maximize distance to opponent; else minimize
        if evader:
            return (d_to_op, -d_to_corner)
        return (-d_to_op, d_to_corner)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        key = score(nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]