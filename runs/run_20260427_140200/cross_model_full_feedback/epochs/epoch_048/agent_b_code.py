def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None
    best_score = -10**9

    def manhattan(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Prefer moving toward nearest resource, then avoid opponent, then center
    def score(pos):
        x, y = pos
        s = 0
        # distance to closest resource
        if resources:
            d = min(manhattan((x,y), r) for r in resources)
            s -= d * 2
        # distance to opponent (want to avoid)
        s -= max(0, manhattan((x,y), (ox, oy)) - 1)
        # distance to center
        cx, cy = w//2, h//2
        s -= abs(x - cx) + abs(y - cy)
        return s

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sc = score((nx, ny))
        if sc > best_score:
            best_score = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]