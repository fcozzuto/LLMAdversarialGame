def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cell_priority(x, y, selfx, selfy):
        # Higher is better
        best = -10**9
        for rx, ry in resources:
            ds = cheb(selfx, selfy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we are closer to; if both can reach, prefer smaller ds.
            p = (do - ds) * 1000 - ds
            if p > best:
                best = p
        return best

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = cell_priority(nx, ny, nx, ny)
        # Tie-break: prefer not moving if scores equal, then prefer staying closer to opponent-blocking positions.
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]