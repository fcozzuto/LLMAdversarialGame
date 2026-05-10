def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    ob = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in role

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in ob

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    man = lambda a, b, c, d: abs(a - c) + abs(b - d)

    if self_is_evader:
        tx, ty = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
    else:
        tx, ty = min(corners, key=lambda c: man(c[0], c[1], ox, oy))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy
        d_new = man(nx, ny, ox, oy)
        d_corner = man(nx, ny, tx, ty)

        if self_is_evader:
            # Primary: maximize distance; Secondary: approach chosen far corner; Tertiary: reduce corner distance tie-break.
            score = (d_new * 1000) - (d_corner)
        else:
            # Primary: minimize distance; Secondary: approach restriction corner; Tertiary: reduce distance to opponent if still tied.
            score = (-d_new * 1000) - (d_corner * 0.5)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]