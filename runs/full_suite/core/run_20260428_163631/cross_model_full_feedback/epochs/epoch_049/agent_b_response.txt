def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target nearest resource, avoiding immediate opponent proximity
    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        score = 0
        if resources:
            # distance to closest resource
            d = min(man((nx, ny), r) for r in resources)
            score -= d
        # penalize proximity to opponent to avoid instant capture
        odist = max(1, abs(nx - ox) + abs(ny - oy))
        score -= max(0, 3 - odist)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]