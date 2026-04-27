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

    base_moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    rot = turn % len(base_moves)
    moves = base_moves[rot:] + base_moves[:rot]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best = None
    bestv = -10**9

    def score_candidate(nx, ny):
        if not free(nx, ny):
            return -10**9
        # Encourage moving toward nearest resource, but also stay reasonably central
        if resources:
            d = min((man((nx,ny), r) for r in resources), default=10**9)
            central = abs(nx - w//2) + abs(ny - h//2)
            return -d + (-central)*0.01
        else:
            # fallback to closeness to opponent to pressure
            dop = man((nx,ny), (ox,oy))
            return -dop

    best_move = (0,0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = score_candidate(nx, ny)
        if v > bestv:
            bestv = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]