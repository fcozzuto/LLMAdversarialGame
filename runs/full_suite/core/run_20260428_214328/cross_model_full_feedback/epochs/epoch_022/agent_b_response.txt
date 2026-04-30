def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles_list = observation.get("obstacles", []) or []
    resources_list = observation.get("resources", []) or []

    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)
    resources = [(int(p[0]), int(p[1])) for p in resources_list]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def collide(nx, ny):
        return (nx, ny) in obstacles or (nx, ny) == (ox, oy)

    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and not collide(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = [0, 0]
    best_score = -10**9

    for dx, dy, nx, ny in legal:
        score = 0
        if (nx, ny) == (ox, oy):
            score -= 1000
        if resources:
            d = min(dist((nx, ny), r) for r in resources)
            score -= d
        # Move toward closest resource if beneficial; otherwise prefer center
        if resources:
            if d <= 2:
                score += 5
        center_dist = max(abs(nx - w//2), abs(ny - h//2))
        score -= center_dist * 0.1

        # Avoid getting too far from opponent if possible: slight bias to keep distance
        od = dist((nx, ny), (ox, oy))
        score += od * 0.01

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move