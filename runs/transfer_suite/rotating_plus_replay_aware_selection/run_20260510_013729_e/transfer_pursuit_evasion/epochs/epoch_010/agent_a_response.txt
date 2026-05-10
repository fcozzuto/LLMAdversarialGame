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

    self_role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in self_role

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    far_corner = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: manh(c[0], c[1], ox, oy))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in ob

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        if self_is_evader:
            corner = far_corner
            key = (d, -manh(nx, ny, corner[0], corner[1]), -manh(sx, sy, ox, oy))
        else:
            corner = near_corner
            key = (-d, manh(nx, ny, corner[0], corner[1]), manh(sx, sy, ox, oy))
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]