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

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist_cheb(a, b):
        dx = abs(a[0]-b[0]); dy = abs(a[1]-b[1])
        return dx if dx>dy else dy

    def sign(a): return -1 if a<0 else (1 if a>0 else 0)

    # If there is a resource, target to maximize (my distance decrease - opponent distance decrease)
    if res:
        best_r = None
        best_key = None
        for rx, ry in res:
            md = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            # Prefer resources closer to me and far from opponent
            key = (md, -od, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        if best_r is not None:
            dx = best_r[0] - sx
            dy = best_r[1] - sy
            dx = max(-1, min(1, dx))
            dy = max(-1, min(1, dy))
            return [dx, dy]

    # No reachable resources or blocked; move to increase distance from opponent while staying valid
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        # simple heuristic: prefer moving away from opponent, then closer to center
        away = (nx - ox, ny - oy)
        dist_opp = abs(away[0]) + abs(away[1])
        dist_center = abs(nx - w//2) + abs(ny - h//2)
        score = (dist_opp, -dist_center)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is not None:
        return [best_move[0], best_move[1]]

    # Fallback: stay
    return [0, 0]