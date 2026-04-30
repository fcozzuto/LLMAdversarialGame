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
    def collide(x, y):
        return (x, y) in obstacles or (x, y) == (ox, oy)
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

    def min_dist_to_resources(x, y):
        if not resources:
            return None
        d = min(dist((x, y), r) for r in resources)
        return d

    # Prefer moving toward nearest resource while avoiding opponent's square and obstacles.
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy, nx, ny in legal:
        score = 0
        # proximity to opponent: try to stay not too close unless capturing opportunity (not implemented)
        odist = dist((nx, ny), (ox, oy))
        if odist == 0:
            score -= 100  # would collide; but collision prevented already
        else:
            score -= odist  # discourage approaching too close
        rdist = min_dist_to_resources(nx, ny)
        if rdist is not None:
            score += max(0, 10 - rdist)  # reward getting closer to resource
        # discourage staying in same spot unless needed
        if dx == 0 and dy == 0:
            score -= 1
        # avoid revisiting obvious traps (simple heuristic)
        if (nx, ny) in obstacles:
            score -= 5
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move