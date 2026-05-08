def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    r = int(observation.get("capture_radius", 0) or 0)

    best_dxdy = [0, 0]
    best_val = None

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        d = cheb(nx, ny, ox, oy)
        if pursuer and d <= r:
            return [dx, dy]

        # Penalty for moving into tight spaces around obstacles.
        near = 0
        for ax, ay in neigh:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in blocked:
                near += 1

        if pursuer:
            # minimize distance; small penalty for near obstacles
            val = (-d * 100) - (near * 3)
            better = (best_val is None) or (val > best_val)
        else:
            # maximize distance; slight penalty for near obstacles and discourage self-cornering
            corner = (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)
            val = (d * 100) - (near * 3) - (corner * 2)
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_dxdy = [dx, dy]

    return best_dxdy