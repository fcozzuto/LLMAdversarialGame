def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("hide" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)

        # Prefer moves that keep distance to opponent; then steer toward farthest corner from opponent.
        # For pursuer, do the opposite: minimize distance to opponent; then nudge toward a corner to reduce escape options.
        if i_am_evader:
            d_far = cheb(nx, ny, far_corner[0], far_corner[1])
            score = (d_op * 1000) - d_far
            # Slightly prefer not moving into immediate obstacle-adjacent squares
            obs_adj = sum(1 for ax, ay in blocked if abs(ax - nx) <= 1 and abs(ay - ny) <= 1)
            score -= obs_adj
        else:
            score = (-d_op * 1000) + (-man(nx, ny, far_corner[0], far_corner[1]))
            obs_adj = sum(1 for ax, ay in blocked if abs(ax - nx) <= 1 and abs(ay - ny) <= 1)
            score -= obs_adj

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]