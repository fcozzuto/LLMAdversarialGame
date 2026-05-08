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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda t: (t[0], t[1]))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        refx, refy = ox, oy
        target = max(corners, key=lambda c: cheb(c[0], c[1], refx, refy))
    else:
        target = None

    best_move = (0, 0)
    if is_evader:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            dist_away = cheb(nx, ny, ox, oy)
            dist_to_corner = cheb(nx, ny, target[0], target[1])
            score = (dist_away, -dist_to_corner, -dx, -dy)
            if best is None or score > best:
                best = score
                best_move = (dx, dy)
    else:
        # Pursuer: minimize distance to evader; lightly prefer moves that also reduce distance to a "good" corner.
        # Choose a deterministic secondary corner: far from our own start (to keep momentum away from edges blocked by obstacles).
        good_corner = max(corners, key=lambda c: cheb(c[0], c[1], sx, sy))
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            dist = cheb(nx, ny, ox, oy)
            corner_bias = cheb(nx, ny, good_corner[0], good_corner[1])
            score = (-dist, -corner_bias, -dx, -dy)
            if best is None or score > best:
                best = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]