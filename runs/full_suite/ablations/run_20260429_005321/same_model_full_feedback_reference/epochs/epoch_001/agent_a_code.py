def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = observation.get('obstacles', []) or []
    obs_set = {tuple(p) for p in obstacles}
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    res = [tuple(p) for p in resources]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    best = (10**9, 0, (0,0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs_set:
            continue
        dres = 10**6
        if res:
            dres = min(dist((nx, ny), r) for r in res)
        dop = dist((nx, ny), (ox, oy))
        # Prefer resources; also prefer separation when opponent is near
        goal = (dres, -dop if dop <= 2 else 0)
        score = dres * 1000 - (dop if dop <= 2 else 0)
        # Tie-break deterministically by ordering (dx,dy) and then center pull
        cx, cy = (w-1)/2.0, (h-1)/2.0
        center_pull = abs(nx - cx) + abs(ny - cy)
        score = score * 100 + int(center_pull)
        # Deterministic tie breaker
        tie = (dx + 1) * 10 + (dy + 1)
        if score < best[0] or (score == best[0] and tie < best[1]):
            best = (score, tie, (dx, dy))
    return [best[2][0], best[2][1]]