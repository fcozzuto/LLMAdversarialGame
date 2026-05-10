def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Deterministic tiebreak: fixed move order
    best_move = moves[4]  # (0,0)
    best_score = None

    if is_evader:
        # maximize distance; secondarily prefer moving toward the farthest corner from pursuer
        far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            corner_term = -cheb(nx, ny, far_corner[0], far_corner[1])  # closer to far corner => larger
            score = (d, corner_term)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        # minimize distance; secondarily block by preferring moves that reduce opponent's distance to nearest corner
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_self = cheb(nx, ny, ox, oy)
            opp_nearest_corner = min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
            block_score = cheb(ox, oy, opp_nearest_corner[0], opp_nearest_corner[1]) - cheb(nx, ny, opp_nearest_corner[0], opp_nearest_corner[1])
            # block_score larger is better; combine by lexicographic
            score = (-d_self, block_score)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move