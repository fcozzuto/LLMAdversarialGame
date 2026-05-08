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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        refx, refy = ox, oy
    else:
        refx, refy = sx, sy
    escape_corner = max(corners, key=lambda c: cheb(c[0], c[1], refx, refy))

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # Evader wants larger distance; pursuer wants smaller distance.
        # Tie-breakers: prefer escape corner (evader) / prefer advancing (pursuer).
        corner_bias = cheb(nx, ny, escape_corner[0], escape_corner[1])
        if is_evader:
            score = (d, -corner_bias, -abs((nx - ox)) - abs((ny - oy)))
            better = best_score is None or score > best_score
        else:
            score = (-d, corner_bias, abs((nx - ox)) + abs((ny - oy)))
            better = best_score is None or score > best_score
        if better:
            best_score = score
            best_move = [dx, dy]

    if best_score is None:
        # If somehow all moves invalid (shouldn't happen), stay.
        return [0, 0]
    return best_move