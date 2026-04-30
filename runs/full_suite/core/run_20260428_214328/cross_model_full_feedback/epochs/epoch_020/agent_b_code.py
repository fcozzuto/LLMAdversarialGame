def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles_list = observation.get("obstacles", []) or []
    resources_list = observation.get("resources", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)
    resources = [(int(p[0]), int(p[1])) for p in resources_list]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def collide(nx, ny):
        return (nx, ny) in obstacles or (nx, ny) == (ox, oy)
    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))
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
        # Avoid stepping onto opponent
        if (nx, ny) == (ox, oy):
            score -= 1000
        # Prefer closer to nearest resource if available
        if resources:
            d = min(dist((nx, ny), r) for r in resources)
            score -= d
        # Slightly discourage approaching opponent too aggressively
        opp_dist = dist((nx, ny), (ox, oy))
        score -= max(0, 2 - (opp_dist))  # small penalty if getting close
        # Reward staying near own starting zone if resources balanced (stable baseline)
        if (nx, ny) == (sx, sy):
            score += 0

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move