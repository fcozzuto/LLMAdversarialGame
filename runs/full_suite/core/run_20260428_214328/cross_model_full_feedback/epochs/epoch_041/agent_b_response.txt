def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and not (nx == ox and ny == oy):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy)

    best_move = None
    best_score = None

    # If there are resources, prioritize closest resource while avoiding opponent and obstacles
    if res:
        for dx, dy, nx, ny in legal:
            # distance to nearest resource
            d = None
            for rx, ry in res:
                cd = dist((nx, ny), (rx, ry))
                if d is None or cd < d:
                    d = cd
            score = -d  # closer to resource is better
            # also discourage moving toward opponent
            od = dist((nx, ny), (ox, oy))
            if od == 0:
                score -= 3
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    # Otherwise, move toward the opponent but with a small bias to keep distance
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        od = dist((nx, ny), (ox, oy))
        score = -od
        # slight bias to diagonals that reduce distance when safe
        if abs(dx) + abs(dy) == 2:
            score += 0.5
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    # Fallback
    return [0, 0]