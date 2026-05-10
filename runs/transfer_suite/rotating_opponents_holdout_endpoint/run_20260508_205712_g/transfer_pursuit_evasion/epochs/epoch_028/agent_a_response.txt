def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = "pursuer" in role or (role == "" and "pursuer" in opp_role and "evader" not in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Candidate evaluation
    best_move = (0, 0)
    best_val = None
    dist_now = cheb(sx, sy, ox, oy)

    # For evader, pick farthest reachable corner from opponent as a secondary target
    corner_target = corners[0]
    best_corner_dist = -1
    for cx, cy in corners:
        if inside(cx, cy):
            d = cheb(cx, cy, ox, oy)
            if d > best_corner_dist:
                best_corner_dist = d
                corner_target = (cx, cy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)

        if is_pursuer:
            # Prefer smaller distance; avoid giving opponent space by slight corner bias
            target_corner_bias = -cheb(nx, ny, corner_target[0], corner_target[1]) * 0.01
            val = -d + target_corner_bias
        else:
            # Prefer larger distance; avoid moving into tight choke near opponent
            corner_bias = cheb(nx, ny, corner_target[0], corner_target[1]) * 0.02
            val = d + corner_bias

        # Tie-break deterministically by smallest lex move
        if best_val is None or (val > best_val + 1e-12) or (abs(val - best_val) <= 1e-12 and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]