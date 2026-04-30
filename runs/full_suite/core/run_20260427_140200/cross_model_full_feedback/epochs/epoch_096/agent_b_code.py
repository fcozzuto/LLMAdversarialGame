def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if resources:
        tx, ty = min(resources, key=lambda p: manh((mx, my), p))
    else:
        tx, ty = (ox, oy)

    best_dx = 0
    best_dy = 0
    best_score = None

    def score_move(dx, dy):
        nx, ny = mx + dx, my + dy
        if not safe(nx, ny):
            return None
        # simple heuristic: move toward target (tx, ty), break ties by staying closer to opponent
        dist_to_target = abs(nx - tx) + abs(ny - ty)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        # want small dist to target and large distance to opponent to avoid conflict
        return ( -dist_to_target, -(dist_to_opp) )

    for dx, dy in moves:
        sc = score_move(dx, dy)
        if sc is None:
            continue
        if best_score is None or sc > best_score:
            best_score = sc
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]