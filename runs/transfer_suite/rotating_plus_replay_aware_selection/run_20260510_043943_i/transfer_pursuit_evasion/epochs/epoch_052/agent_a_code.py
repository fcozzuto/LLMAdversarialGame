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
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self and "evade" not in role_self)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    far_corner = max(corners, key=lambda c: cheb(sx, sy, c[0], c[1]) + cheb(c[0], c[1], ox, oy))
    # For evader, prefer moving away from opponent and towards far_corner; for pursuer opposite.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, far_corner[0], far_corner[1])
        # Capture radius 0: moving onto opponent wins immediately if pursuer; avoid if evader.
        if (nx, ny) == (ox, oy):
            score = 10**9 if not is_evader else -10**9
        else:
            score = (d_opp * (1 if is_evader else -1)) + (d_corner * (-0.6 if is_evader else 0.6))
        if best_score is None or (score > best_score if is_evader else score < best_score):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]