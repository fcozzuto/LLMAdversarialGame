def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    self_role = observation.get("self_role", "") or ""
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    target_corner = min(corners, key=lambda c: d2(c[0], c[1], ox, oy))  # closest corner to opponent
    corners_sorted = sorted(corners, key=lambda c: d2(c[0], c[1], sx, sy))

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = d2(nx, ny, ox, oy)
        # Count available next squares (prefer not to get boxed in)
        free_neighbors = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                free_neighbors += 1

        if self_role.lower().startswith("evader"):
            # Run away; also push toward the opposite corner (relative to opponent)
            far_corner = max(corners, key=lambda c: d2(c[0], c[1], ox, oy))
            corner_bias = d2(nx, ny, far_corner[0], far_corner[1])
            score = (-d_opp, corner_bias, -free_neighbors, nx, ny)
        else:
            # Chase; also slightly bias toward cornering the opponent (reduce their best-corner escape)
            corner_escape = d2(nx, ny, target_corner[0], target_corner[1])
            score = (d_opp, corner_escape, -free_neighbors, nx, ny)

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move