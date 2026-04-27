def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    base_moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    rot = turn % len(base_moves)
    moves = base_moves[rot:] + base_moves[:rot]

    best = [0,0]
    bestv = -10**9

    def score_candidate(nx, ny):
        if not free(nx, ny):
            return -10**9
        # Prefer moving toward closest resource that is closer to me than to opponent
        if resources:
            d_me = min((man((nx,ny), (int(rx), int(ry))) for rx, ry in resources), default=10**9)
            d_opp = min((man((nx,ny), (ox, oy)) for _ in [0]), default=10**9)
            # heuristic: bring me closer to resource if better than opponent
            s = -d_me
            if d_me < d_opp:
                s += 2
            return s
        # otherwise head toward center, with slight bias toward opponent distance to stay away
        center_dist = man((nx, ny), ((w-1)//2, (h-1)//2))
        away_from_opp = man((nx, ny), (ox, oy))
        return -center_dist - (away_from_opp < 3 and 0) + away_from_opp*0  # neutral but keeps determinism

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = score_candidate(nx, ny)
        if val > bestv:
            bestv = val
            best = [dx, dy]

    return best