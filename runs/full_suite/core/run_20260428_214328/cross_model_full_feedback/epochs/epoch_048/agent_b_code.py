def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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
    best = (0, 0)
    best_score = -10**18

    target = None
    if res:
        # closest resource
        target = min(res, key=lambda p: dist((sx, sy), p))

    def near_to_opp(px, py):
        return dist((px, py), (ox, oy))

    # Simple deterministic scoring: prefer moving toward closest resource not blocked,
    # but avoid stepping onto opponent's cell. If blocked, try to stay or sidestep.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        if (nx, ny) == (ox, oy):
            # discourage moving into opponent
            score = -1000
        else:
            score = 0
            if target is not None:
                score -= dist((nx, ny), target)
                # prefer being closer to target
            # also encourage staying closer to opponent to contest
            score += -0.5 * near_to_opp(nx, ny)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    # Fallback: if no move found (should not happen), stay.
    return [int(best[0]), int(best[1])]