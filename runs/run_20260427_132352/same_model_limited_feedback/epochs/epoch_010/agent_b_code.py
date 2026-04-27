def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((x, y) for x, y in obstacles)
    def cheb(a, b): 
        return abs(a[0]-b[0]) if a[0]!=b[0] else abs(a[1]-b[1])
    def dist(p, q): 
        dx = abs(p[0]-q[0]); dy = abs(p[1]-q[1])
        return dx if dx > dy else dy

    # pick nearest resource by deterministic tie-break
    if resources:
        target = None
        bestd = 10**9
        for r in resources:
            d = dist((sx, sy), r)
            if d < bestd or (d == bestd and (r[0], r[1]) < (target[0], target[1])):
                bestd = d
                target = r
    else:
        target = (ox, oy)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue
            moves.append((dx, dy, nx, ny))

    # score: minimize distance to target, then keep away from opponent, then prefer forward/diagonal
    best = None
    bestscore = -10**18
    for dx, dy, nx, ny in moves:
        d_to_t = dist((nx, ny), target)
        d_op = dist((nx, ny), (ox, oy))
        # prefer reducing distance; slight preference for diagonal and toward target direction
        pref_diag = 1 if dx != 0 and dy != 0 else 0
        dirx = 1 if nx > sx else (-1 if nx < sx else 0)
        diry = 1 if ny > sy else (-1 if ny < sy else 0)
        toward = 1 if ((target[0]-sx) * dirx >= 0 and (target[1]-sy) * diry >= 0) else 0
        score = (-d_to_t * 100) + (d_op * 1.5) + (pref_diag * 0.2) + (toward * 0.05) - (abs(dx)+abs(dy))*0.01
        if score > bestscore or (score == bestscore and (dx, dy) < (best[0], best[1])):
            bestscore = score
            best = (dx, dy, nx, ny)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]