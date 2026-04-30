def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    safe_moves = []
    for dx, dy, nx, ny in legal:
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            continue
        safe_moves.append((dx, dy, nx, ny))

    if not safe_moves:
        safe_moves = legal

    if resources:
        best = None
        best_score = None
        for dx, dy, nx, ny in safe_moves:
            rdist = min(dist((nx, ny), r) for r in resources)
            harmful = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)
            score = -rdist
            if harmful:
                score -= 100  # discourage approaching near opponent
            if best is None or score > best_score:
                best = (dx, dy, nx, ny)
                best_score = score
        if best is not None:
            return [best[0], best[1]]

    # Fallback: move away from opponent if possible, else toward center
    best_move = None
    best_pull = None
    for dx, dy, nx, ny in safe_moves:
        pull = dist((nx, ny), (ox, oy))
        if best_pull is None or pull > best_pull:
            best_pull = pull
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    return [0, 0]