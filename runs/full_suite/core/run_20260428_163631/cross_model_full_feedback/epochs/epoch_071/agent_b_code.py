def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
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

    # Target the closest resource, with tie-breaking preferring positions closer to center
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = manh(sx, sy, rx, ry)
            dk = abs(rx - w//2) + abs(ry - h//2)
            key = (ds, dk, rx, ry)
            if best is None or key < best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
        # choose move that brings us closest to (tx,ty)
        best_move = None
        best_dist = None
        for dx, dy, nx, ny in legal:
            d = manh(nx, ny, tx, ty)
            if best_move is None or d < best_dist:
                best_move = (dx, dy)
                best_dist = d
        if best_move is not None:
            return [best_move[0], best_move[1]]

    # If no resources reachable or considered, head toward center while avoiding opponent
    center_x, center_y = w//2, h//2
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        dist_to_center = manh(nx, ny, center_x, center_y)
        dist_to_opp = manh(nx, ny, ox, oy)
        # prefer closer to center and far from opponent
        score = (dist_to_center, -dist_to_opp)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    # fallback
    return [0, 0]