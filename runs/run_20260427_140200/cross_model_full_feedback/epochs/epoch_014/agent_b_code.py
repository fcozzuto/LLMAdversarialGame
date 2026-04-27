def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Simple deterministic heuristic:
    #  - prioritize moves that get closer to the nearest resource
    #  - tiebreak by staying or moving toward opponent to contest
    best = None
    bestv = -10**9

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    nearest = None
    minr = 10**9
    for r in resources:
        d = dist((sx, sy), r)
        if d < minr:
            minr = d
            nearest = r

    for dx, dy, nx, ny in cand:
        v = 0
        if nearest is not None:
            v -= dist((nx, ny), nearest) * 2  # get closer to resource
        v -= dist((nx, ny), (ox, oy))  # approach opponent
        # prefer moving closer to center when no resource
        cx, cy = w//2, h//2
        v -= abs(nx - cx) + abs(ny - cy)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]