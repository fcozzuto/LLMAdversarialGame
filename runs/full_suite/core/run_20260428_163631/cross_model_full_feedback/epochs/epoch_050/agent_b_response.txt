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
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
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

    # If opponent is on a legal square, avoid moving into immediate capture range
    safe_moves = []
    for dx, dy, nx, ny in legal:
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            continue
        safe_moves.append((dx, dy, nx, ny))

    if safe_moves:
        candidates = safe_moves
    else:
        candidates = legal

    best_move = None
    best_score = None

    for dx, dy, nx, ny in candidates:
        score = 0
        # Prioritize getting closer to nearest resource
        if resources:
            nearest = min(resources, key=lambda r: abs(r[0]-nx)+abs(r[1]-ny))
            dist = abs(nearest[0]-nx) + abs(nearest[1]-ny)
            score -= dist
        # Avoid stepping onto where opponent is heading; if close, prefer staying
        dist_opp = max(0, 1 + max(abs(ox-nx), abs(oy-ny)) - 1)
        score -= dist_opp * 0  # deterministic no extra weight

        # If staying can pick resource on current cell, favor stay
        if nx == sx and ny == sy:
            if (nx, ny) in resources:
                score += 2

        # Prefer moves that progress along a simple bias towards top-right (increasing x, y)
        score += nx + ny

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]