def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    mx, my = int(observation.get("self_position")[0]), int(observation.get("self_position")[1])
    ox, oy = int(observation.get("opponent_position")[0]), int(observation.get("opponent_position")[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = observation.get("resources") or []
    resources = []
    for r in res:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # Target: if there is any resource, head toward closest resource; else head toward opponent
    if resources:
        tx, ty = min(resources, key=lambda p: manh((mx, my), p))
    else:
        tx, ty = (ox, oy)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not safe(nx, ny):
            continue
        d_to_target = manh((nx, ny), (tx, ty))
        d_to_opp = manh((nx, ny), (ox, oy))
        # Score prioritizes getting closer to target, while also considering staying away from opponent
        score = (-d_to_target, d_to_opp, dx, dy)
        if best is None or score < best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]