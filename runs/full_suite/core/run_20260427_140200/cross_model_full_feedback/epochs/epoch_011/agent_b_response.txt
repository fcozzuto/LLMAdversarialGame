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
        obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = [(int(r[0]), int(r[1])) for r in resources if r is not None and len(r) >= 2]

    base_moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Deterministic rotation based on turn
    rot = turn % len(base_moves)
    moves = base_moves[rot:] + base_moves[:rot]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best = [0,0]
    bestv = -10**9

    def score_candidate(nx, ny):
        if not free(nx, ny):
            return -10**9
        # Prefer getting closer to any resource, but also consider staying near center
        if res:
            d_me = min((man((nx,ny), (rx, ry)) for rx, ry in res), default=10**9)
            d_opp = man((nx, ny), (ox, oy))
            s = -d_me
            # reward being closer to resource than opponent
            if d_me < d_opp:
                s += 5
            return s
        # no resources: move toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return -man((nx, ny), (cx, cy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            v = score_candidate(nx, ny)
            if v > bestv:
                bestv = v
                best = [dx, dy]

    return best