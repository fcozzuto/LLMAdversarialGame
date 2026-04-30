def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        best_score = -10**18
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            # Prefer resources we're closer to; break ties by closer overall and stable ordering.
            score = (do - ds) * 1000 - ds * 3 + (x - y) * 0
            if score > best_score or (score == best_score and (ds < cheb(sx, sy, best[0], best[1]) if best else True)):
                best_score = score
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    # Greedy step: minimize distance to target, with deterministic obstacle-aware tie-breaking.
    # If moving too greedily would get us closer but into "danger" near opponent, add penalty.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        d_now = cheb(sx, sy, tx, ty)
        # Value: want smaller d1, and (slightly) prefer staying farther from opponent to avoid contest.
        val = -d1 * 10 + d_opp * 0.1 + (d_now - d1) * 2
        # Deterministic tie-break: prefer (0,0), then smallest dx, then smallest dy.
        if val > best_val or (val == best_val and ((dx, dy) == (0, 0) or dx < best_move[0] or (dx == best_move[0] and dy < best_move[1]))):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]