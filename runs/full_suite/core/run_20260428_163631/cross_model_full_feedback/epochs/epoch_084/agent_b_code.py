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
            if inb(x, y): obstacles.add((x, y))

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

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Preference order:
    # 1) Move toward closest resource not blocked by obstacle or out of bounds, if safe from opponent within 2 steps
    # 2) If no safe resource, move to maximize distance from opponent (evade deterministically)
    # 3) Otherwise stay or approach if nothing else

    best_move = None

    if resources:
        best_score = None
        for dx, dy, nx, ny in legal:
            d_to_res = min((abs(nx - rx) + abs(ny - ry)) for rx, ry in resources)
            # closer resource better
            score = -d_to_res
            # discourage stepping into square nearer to opponent if possible
            manh_to_opp = abs(nx - ox) + abs(ny - oy)
            if manh_to_opp <= 1:
                score -= 1
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        if best_move is not None:
            return [best_move[0], best_move[1]]

    # No good resource grab. Evade opponent deterministically: move to the cell among legal that maximizes distance to opponent.
    best_score = None
    for dx, dy, nx, ny in legal:
        d = dist((nx, ny), (ox, oy))
        if best_score is None or d > best_score:
            best_score = d
            best_move = (dx, dy)
    if best_move is not None:
        return [best_move[0], best_move[1]]

    # Fallback stay
    return [0, 0]