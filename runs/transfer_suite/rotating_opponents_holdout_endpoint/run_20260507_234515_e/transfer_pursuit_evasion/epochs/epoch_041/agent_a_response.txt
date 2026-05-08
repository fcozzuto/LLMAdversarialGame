def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role", "") or "").lower()
    self_is_pursuer = ("purs" in role) or (role == "")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in oset

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def nearest_corner_d(x, y):
        return min(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    best = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        if self_is_pursuer:
            # Primary: minimize pursuer-opponent distance; Secondary: move opponent "closer to corners"
            key = (d, nearest_corner_d(ox, oy), abs(nx - ox) + abs(ny - oy))
        else:
            # Evader: maximize distance; Secondary: avoid giving pursuer easy access (keep your own corner distance large)
            key = (-d, nearest_corner_d(nx, ny), -abs(nx - ox) - abs(ny - oy))
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]