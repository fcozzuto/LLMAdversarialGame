def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    # Determine "away" direction (used when urgent for evader)
    away_dx = -1 if ox > sx else (1 if ox < sx else 0)
    away_dy = -1 if oy > sy else (1 if oy < sy else 0)

    best = None
    best_score = None

    d_now = cheb(sx, sy, ox, oy)
    urgent = is_evader and d_now <= 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        if not is_evader:
            # pursuer: greedily close, with small tie-break to avoid wasting moves
            score = -d_opp
            if d_opp == 0:
                score += 1000
            # slight preference to align movement toward opponent
            score += -0.01 * (abs(nx - ox) + abs(ny - oy))
        else:
            # evader: maximize distance; also drift toward farthest corner
            score = d_opp
            score += 0.03 * cheb(nx, ny, far_corner[0], far_corner[1])
            # discourage stepping into alignment that lets pursuer mirror (row/col)
            same_row = 1 if ny == oy else 0
            same_col = 1 if nx == ox else 0
            score -= 0.15 * (same_row + same_col)
            if urgent:
                # in urgent situations, move directly away if possible
                score += 0.25 * (dx * away_dx + dy * away_dy)

        # deterministic tie-break: prefer smallest (dx,dy) lexicographically after score
        key = (score, -abs(cheb(nx, ny, far_corner[0], far_corner[1])) if is_evader else 0, -cheb(nx, ny, ox, oy), dx, dy)
        if best is None or key > best:
            best = key
            best_score = score

    if best is None:
        return [0, 0]
    # Recover chosen move from tie-break components stored in best
    return [int(best[3]), int(best[4])]