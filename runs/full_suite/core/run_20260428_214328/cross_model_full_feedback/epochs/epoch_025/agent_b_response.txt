def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles_list = observation.get("obstacles", []) or []
    resources_list = observation.get("resources", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)
    resources = [(int(p[0]), int(p[1])) for p in resources_list]

    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def collide(nx, ny):
        return (nx, ny) in obstacles or (nx, ny) == (ox, oy)

    # 8-directional moves plus stay
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and not collide(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    best = None
    best_score = -10**9

    for dx, dy, nx, ny in legal:
        score = 0
        # Avoid opponent
        if (nx, ny) == (ox, oy):
            score -= 1000

        # Distance to nearest resource
        if resources:
            dmin = min(dist((nx, ny), (rx, ry)) for rx, ry in resources)
            # Prefer moving closer to resources
            score -= dmin

        # If on resource, gain small reward
        if resources:
            if (nx, ny) in resources:
                score -= 0  # neutral; resource pickup handled by game scoring
        # If moving toward opponent's goal could be risky; keep deterministic bias to closer to resources
        if scores := observation.get("scores"):
            pass

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]