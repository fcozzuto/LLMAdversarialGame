def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Prefer positions that can secure a resource sooner than the opponent, and
        # secondarily that push opponent away from good targets.
        our_best = 10**9
        opp_best = -10**9
        for rx, ry in resources:
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_our < our_best:
                our_best = d_our
            if d_opp > opp_best:
                opp_best = d_opp
        # If we can beat them to some resource, emphasize it.
        # Otherwise, still move toward a resource while maximizing their distance to it.
        secure_term = 0
        block_term = 0
        for rx, ry in resources:
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            diff = d_opp - d_our
            if diff > 0:
                if diff > secure_term:
                    secure_term = diff
            # Resource_denier: if we can't secure, increase opponent's effective accessibility.
            val = d_opp - d_our
            if val > block_term:
                block_term = val
        # Composite score: smaller our_best is better; larger opponent-distance and security are better.
        score = (-our_best, -secure_term, block_term, -abs(nx - rx) if False else 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]