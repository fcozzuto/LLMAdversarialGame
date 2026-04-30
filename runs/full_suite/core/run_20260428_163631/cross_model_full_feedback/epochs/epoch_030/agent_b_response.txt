def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obst.add((px, py))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obst:
                resources.append((rx, ry))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    # If no resources visible, head toward opponent to contest
    if not resources:
        best = None
        best_score = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d_self = dist((nx, ny), (sx, sy))  # will be 1 or sqrt-like; keep simple
            d_opp = dist((nx, ny), (ox, oy))
            score = d_opp - d_self
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        if best is None:
            return [0,0]
        return [best[0], best[1]]

    # Target nearest resource with simple heuristic
    best_move = None
    best_metric = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # distance to closest resource after move
        if resources:
            d = min(dist((nx, ny), r) for r in resources)
        else:
            d = dist((nx, ny), (ox, oy))
        # proximity to opponent after move
        od = dist((nx, ny), (ox, oy))
        metric = (d * 2) - od  # prefer closer to resource and closer to opponent (contest)
        if best_metric is None or metric > best_metric:
            best_metric = metric
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]