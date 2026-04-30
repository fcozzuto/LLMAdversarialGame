def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    if resources:
        # Move toward closest resource if safe
        best_score = None
        for dx, dy, nx, ny in legal:
            d_to_res = min((abs(nx - rx) + abs(ny - ry)) for rx, ry in resources)
            score = -d_to_res
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # If no resources or no safe target, try to stay close to center while avoiding opponent
    target_x, target_y = w // 2, h // 2
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        d_to_center = dist((nx, ny), (target_x, target_y))
        d_to_opp = dist((nx, ny), (ox, oy))
        # Prefer moving toward center and away from opponent
        score = -d_to_center + d_to_opp
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # Fallback to moving away from opponent when possible
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        score = dist((nx, ny), (ox, oy))  # farther from opponent is better
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]