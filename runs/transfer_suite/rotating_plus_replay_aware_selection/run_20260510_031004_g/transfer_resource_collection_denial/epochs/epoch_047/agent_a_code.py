def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Choose resource where we are (deterministically) more likely to arrive first.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (ds - 2 * do, ds, rx, ry)
        if best is None or score < best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    # If already on target, don't waste a move.
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # One-step greedy toward chosen target.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        dist = cheb(nx, ny, tx, ty)
        # Small preference for moves that also reduce distance from opponent (avoid their grabs).
        opp_dist = cheb(nx, ny, ox, oy)
        key = (dist, opp_dist, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)
    return [int(best_move[1]), int(best_move[2])]