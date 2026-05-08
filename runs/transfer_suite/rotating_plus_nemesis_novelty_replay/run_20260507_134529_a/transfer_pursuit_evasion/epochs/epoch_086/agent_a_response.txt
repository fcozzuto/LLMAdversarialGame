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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda t: (t[0], t[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Preferred corner for evader: farthest corner from the pursuer (our opponent if we are pursuer; else from us)
    if is_evader:
        refx, refy = ox, oy
    else:
        refx, refy = sx, sy
    target_corner = max(corners, key=lambda c: cheb(c[0], c[1], refx, refy))

    best = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, target_corner[0], target_corner[1])
        if is_evader:
            # Run away and also get closer to the chosen corner to corner the evader
            score = (-(d_opp), d_corner)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # Chase while angling toward the evader's corner
            score = (d_opp, d_corner)
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)

    return [best[0], best[1]]