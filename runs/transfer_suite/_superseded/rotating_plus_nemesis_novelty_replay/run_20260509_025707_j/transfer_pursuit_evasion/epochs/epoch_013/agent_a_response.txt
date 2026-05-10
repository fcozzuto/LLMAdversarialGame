def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position")
    op = observation.get("opponent_position")
    if not isinstance(sp, (list, tuple)) or not isinstance(op, (list, tuple)) or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    role = (observation.get("self_role") or "pursuer").lower()
    is_evader = (role == "evader")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist(nx, ny, ox, oy)
        # Tie-breakers: for pursuer prefer moves that reduce opponent distance and increase corner pressure.
        # For evader prefer increasing distance and moving toward a corner farthest from pursuer.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        corner_farthest = max(corners, key=lambda c: dist(c[0], c[1], ox, oy))
        corner_nearest = min(corners, key=lambda c: dist(c[0], c[1], ox, oy))
        if is_evader:
            target = corner_farthest
            val = (-d, dist(nx, ny, target[0], target[1]))
            # minimize negative d == maximize d; then maximize progress to target
            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]
        else:
            target = corner_nearest
            val = (d, dist(nx, ny, target[0], target[1]))
            # minimize d; then minimize distance to target corner to corner-trap
            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]