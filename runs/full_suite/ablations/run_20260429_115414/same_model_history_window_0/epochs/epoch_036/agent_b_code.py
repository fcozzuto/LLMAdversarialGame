def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    if not resources:
        tx, ty = ox, oy
        best = None
        bestv = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = cheb((nx, ny), (tx, ty))
            if v < bestv:
                bestv = v; best = [dx, dy]
        return best if best is not None else [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb((sx, sy), (rx, ry))
        do = cheb((ox, oy), (rx, ry))
        # Prefer resources we can reach no later than opponent; otherwise prefer where opponent is farther
        key = (0 if ds <= do else 1, ds if ds <= do else -do, ds - do)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    cur_opp = cheb((sx, sy), (ox, oy))
    best = [0, 0]
    bestv = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Primary: get closer to target; Secondary: don't drift into opponent too much
        v = cheb((nx, ny), (rx, ry))
        oppd = cheb((nx, ny), (ox, oy))
        if oppd < cur_opp:
            v += 0.25 * (cur_opp - oppd)  # small cost for approaching opponent
        elif oppd > cur_opp:
            v -= 0.05 * (oppd - cur_opp)  # small bonus for spacing
        # Tertiary deterministic tie-breaker: lexicographic on move
        if v < bestv or (v == bestv and [dx, dy] < best):
            bestv = v
            best = [dx, dy]
    return best if best is not None else [0, 0]