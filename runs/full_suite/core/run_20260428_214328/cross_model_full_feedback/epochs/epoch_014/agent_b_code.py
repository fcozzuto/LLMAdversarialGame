def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles_list = observation.get("obstacles", []) or []
    resources_list = observation.get("resources", []) or []

    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)
    resources = [(int(p[0]), int(p[1])) for p in resources_list]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def collide(x, y):
        return (x, y) in obstacles or (x, y) == (ox, oy)

    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    # If there are resources, head towards nearest resource while avoiding opponent and obstacles
    if resources:
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or collide(nx, ny):
                continue
            # distance to nearest resource from (nx,ny)
            d = None
            for rx, ry in resources:
                if not inside(rx, ry) or (rx, ry) in obstacles:
                    continue
                d2 = dist((nx, ny), (rx, ry))
                if d is None or d2 < d:
                    d = d2
            if d is None:
                continue
            # discourage moving into opponent's adjacent zone
            bonus = -0.5 if abs((nx) - ox) + abs((ny) - oy) <= 1 else 0.0
            score = -d + bonus
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # Fallback: move to reduce Chebyshev distance to opponent while staying safe
    best = (0, 0)
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or collide(nx, ny):
            continue
        d = max(abs(nx - ox), abs(ny - oy))
        if best_dist is None or d < best_dist:
            best_dist = d
            best = (dx, dy)
    return [best[0], best[1]]