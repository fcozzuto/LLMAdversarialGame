def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

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

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target closest resource if available, else center move while keeping distance from opponent
    if resources:
        best = None
        best_d = None
        for rx, ry in resources:
            d = manh(sx, sy, rx, ry)
            if best is None or d < best_d:
                best = (rx, ry)
                best_d = d
        tx, ty = best
        # choose move that reduces distance to target
        chosen = None
        best_ld = None
        for dx, dy, nx, ny in legal:
            ld = manh(nx, ny, tx, ty)
            if best_ld is None or ld < best_ld:
                best_ld = ld
                chosen = (dx, dy)
        if chosen is not None:
            return [chosen[0], chosen[1]]

    # Fallback: move toward center while avoiding opponent
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        # prefer increasing distance from opponent slightly but head toward center
        dist_opp = manh(nx, ny, ox, oy)
        dist_center = -abs(nx - cx) - abs(ny - cy)
        score = dist_opp - dist_center
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # Last resort stay
    return [0, 0]