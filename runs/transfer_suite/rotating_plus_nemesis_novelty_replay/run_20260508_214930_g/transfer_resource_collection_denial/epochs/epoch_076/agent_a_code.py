def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0]); ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def opp_best_dist(tx, ty):
        best = 10**9
        for odx, ody in deltas:
            nx, ny = ox + odx, oy + ody
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                if d < best:
                    best = d
        return best

    best_move = (0, 0); best_score = -10**18
    for dx, dy, nx, ny in moves:
        if (nx, ny) in resources:
            return [dx, dy]  # immediate collection
        local = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = opp_best_dist(rx, ry)
            # Prefer states where we beat the opponent to the same resource; tie-break by smaller myd.
            score = (opd - myd) * 100 - myd
            if local is None or score > local[0] or (score == local[0] and myd < local[1]):
                local = (score, myd)
        if local and (local[0] > best_score):
            best_score = local[0]
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]