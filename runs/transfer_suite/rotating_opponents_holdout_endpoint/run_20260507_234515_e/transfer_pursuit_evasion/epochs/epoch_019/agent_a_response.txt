def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("chase" in srole) or ("seeker" in srole) or ("catch" in srole)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    def corner_score(x, y):
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            d = (abs(x - cx) + abs(y - cy))
            if best is None or d > best:
                best = d
        return best if best is not None else 0

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dxdy = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        d = cheb(nx, ny)
        # pursuer: minimize distance; evader: maximize distance
        base = -d if is_pursuer else d
        # encourage evader to keep to farthest corner, discourage pursuer from corner-hiding
        c = corner_score(nx, ny)
        val = base + (0.05 * c if not is_pursuer else -0.03 * c)

        if best_val is None or (val > best_val) or (val == best_val and (dx, dy) < best_dxdy):
            best_val = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]