def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    evader = ("evader" in sr) or ("escape" in sr) or ("runner" in sr)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner_key = max if not evader else min
    target_corner = corner_key(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    best_move = [0, 0]
    if evader:
        best_score = None  # higher is better
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in blocked:
                continue
            d = cheb(nx, ny, ox, oy)
            tc = cheb(nx, ny, target_corner[0], target_corner[1])
            # maximize distance to pursuer, then maximize progress toward good corner (closer to target)
            score = (d, -tc)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        best_score = None  # lower is better (distance), then better tie-breaks
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in blocked:
                continue
            d = cheb(nx, ny, ox, oy)
            # tie-break: also aim to reduce opponent's distance to a corner (net trap)
            opp_corner = corner_key(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
            trap = cheb(ox, oy, opp_corner[0], opp_corner[1]) - cheb(ox, oy, 0, 0)  # deterministic small bias
            score = (d, trap)
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]