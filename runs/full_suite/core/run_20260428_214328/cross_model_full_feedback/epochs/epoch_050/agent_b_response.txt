def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))

    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y):
                obst.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y) and (x, y) not in obst:
                res.append((x, y))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    target = None
    if res:
        target = min(res, key=lambda p: dist((sx, sy), p))

    def near_to_opp(px, py):
        return dist((px, py), (ox, oy))

    # Score: move toward closest resource not blocked and not stepping into obstacles,
    # while staying reasonably away from opponent. If no resource, prefer center-ish stay/move
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        # base score
        score = 0
        if target is not None:
            score -= dist((nx, ny), target) * 2
            score -= dist((nx, ny), (sx, sy))
        else:
            # center preference
            cx, cy = w//2, h//2
            score -= dist((nx, ny), (cx, cy))
        # discourage moving toward opponent
        odist = dist((nx, ny), (ox, oy))
        score -= max(0, (8 - odist))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # Fallback: if best_move leads into obstacle due to edge cases, stay still
    fx, fy = sx + best_move[0], sy + best_move[1]
    if not inside(fx, fy) or (fx, fy) in obst:
        best_move = (0, 0)
    return [int(best_move[0]), int(best_move[1])]