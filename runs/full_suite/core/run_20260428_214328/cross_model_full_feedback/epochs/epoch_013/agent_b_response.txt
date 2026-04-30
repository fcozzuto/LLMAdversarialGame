def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
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

    # If there are resources, head towards closest visible resource while avoiding opponent and obstacles
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
                dist_to_r = dist((nx, ny), (rx, ry))
                if d is None or dist_to_r < d:
                    d = dist_to_r
            if d is None:
                d = 0
            # Prefer smaller distance to a resource, but keep safe from opponent
            opp_dist = dist((nx, ny), (ox, oy))
            score = (d * 2) - opp_dist
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # No resource path found or no valid move towards resource: simple defensive/neutral policy
    # Try to move toward center of board to optimize options, avoiding opponent and obstacles
    cx, cy = w // 2, h // 2
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or collide(nx, ny):
            continue
        # Prefer positions farther from opponent when possible
        my_to_center = dist((nx, ny), (cx, cy))
        opp_to_center = dist((ox, oy), (cx, cy))
        # simple heuristic: minimize distance to center but keep distance from opponent
        away_from_opp = dist((nx, ny), (ox, oy))
        score = (my_to_center) - (away_from_opp // 2)
        if best_val is None or score < best_val:
            best_val = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # Fallback: stay
    return [0, 0]