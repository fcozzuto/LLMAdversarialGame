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

    # If no resources, head toward center near opponent but avoid clash
    best = None
    bestv = -10**9

    def score_candidate(nx, ny):
        if not free(nx, ny):
            return -10**9
        # prioritize closer to nearest resource; if none, small bias toward center
        if resources:
            d = min(man((nx,ny), r) for r in resources)
            return -d
        cx, cy = w/2, h/2
        return -((nx - cx)**2 + (ny - cy)**2)

    # Choose best move by evaluating immediate next-step benefit
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        v = score_candidate(nx, ny)
        # discourage moving into opponent's cell directly (but still allowed if not blocked)
        if (nx, ny) == (ox, oy):
            v -= 5
        if best is None or v > bestv:
            best = (dx, dy)
            bestv = v

    if best is None:
        # fallback stay
        return [0,0]
    return [best[0], best[1]]