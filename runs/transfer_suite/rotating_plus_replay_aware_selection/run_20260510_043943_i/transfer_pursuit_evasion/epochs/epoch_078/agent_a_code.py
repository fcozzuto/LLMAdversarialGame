def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If we are the pursuer, chase with obstacle-aware tie-break.
    # If we are the evader, run toward the farthest corner and away from opponent.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = corners[0]
    best = -1
    for cx, cy in corners:
        d = cheb(cx, cy, ox, oy)
        if d > best:
            best = d
            far_corner = (cx, cy)

    tx, ty = (far_corner[0], far_corner[1]) if is_evader else (ox, oy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_tar = cheb(nx, ny, tx, ty)

        # Count immediate obstacle-free mobility (deterministic, small lookahead).
        mobility = 0
        for ddx, ddy in dirs:
            mx, my = nx + ddx, ny + ddy
            if valid(mx, my):
                mobility += 1

        # Score: higher is better.
        if is_evader:
            score = (d_opp * 20) + (d_tar * 2) + mobility
        else:
            score = (-d_opp * 20) + (-d_tar * 2) + mobility

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]