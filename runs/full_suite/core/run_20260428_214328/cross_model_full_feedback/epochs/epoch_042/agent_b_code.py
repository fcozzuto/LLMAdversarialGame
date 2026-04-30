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
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    best_move = None
    best_score = None

    # Prioritize resources if available
    if res:
        for dx, dy, nx, ny in legal:
            # distance to nearest resource
            d = min(dist((nx, ny), r) for r in res)
            # also prefer staying if resource is directly there
            score = -d
            # also discourage moving into opponent's immediate vicinity
            if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
                score -= 0.5
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        if best_move is not None:
            return best_move

    # If no resource path, move to maximize distance from opponent while staying safe and aiming toward center
    center_x, center_y = w // 2, h // 2
    for dx, dy, nx, ny in legal:
        # prefer moves that bring us closer to center while staying away from opponent
        to_center = -dist((nx, ny), (center_x, center_y))
        away_opp = dist((nx, ny), (ox, oy))
        score = to_center + away_opp * 0.5
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    if best_move is not None:
        return best_move

    # Fallback
    return [0, 0]