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
            dmin = min(dist((nx, ny), r) for r in resources)
            score -= dmin
        # Prefer moving toward nearest resource if not too close to opponent
        if resources:
            closest = min(resources, key=lambda r: dist((nx, ny), r))
            if dist((nx, ny), closest) < dist((sx, sy), closest):
                score += 5
        # If close to opponent, favor escape or block
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            score -= 2

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move