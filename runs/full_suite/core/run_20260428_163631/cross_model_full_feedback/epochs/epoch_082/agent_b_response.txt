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
            if inb(x, y):
                obstacles.add((x, y))

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

    # Target closest resource if available, else move toward opponent to pressure
    best_move = None
    if resources:
        best_score = None
        for dx, dy, nx, ny in legal:
            d_to_res = min((abs(nx - rx) + abs(ny - ry)) for rx, ry in resources)
            opp_dist = dist((nx, ny), (ox, oy))
            score = -d_to_res - opp_dist
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        if best_move is not None:
            return best_move

    # If no resources or no good move toward them, try to stay near center while avoiding capture
    # Move to reduce Manhattan distance to center (3,3) for 8x8 grid
    cx, cy = 3, 3
    best_score = None
    for dx, dy, nx, ny in legal:
        center_dist = abs(nx - cx) + abs(ny - cy)
        opp_dist = dist((nx, ny), (ox, oy))
        score = -center_dist - opp_dist
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    if best_move is not None:
        return best_move

    return [0, 0]