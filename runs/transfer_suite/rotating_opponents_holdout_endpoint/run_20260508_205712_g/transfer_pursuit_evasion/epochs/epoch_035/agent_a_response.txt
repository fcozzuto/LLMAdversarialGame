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
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in role) or (("pursuer" in opp_role) and ("evader" not in role))
    if ("evader" in role) and ("pursuer" not in role):
        pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def corner_target_score(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = -10**9
        for cx, cy in corners:
            d = cheb(cx, cy, x, y)
            if d > best: best = d
        return best

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)
        if pursuer:
            # Prefer reducing capture distance; if tie, prefer moving toward center.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = -(abs(nx - cx) + abs(ny - cy))  # higher is better
            key = (d, -center_bias)  # minimize d, then maximize center_bias
        else:
            # Evader: maximize distance; if tie, prefer farthest corner away from opponent.
            dist_corner = corner_target_score(nx, ny)
            key = (-d, -dist_corner)  # maximize d, then maximize dist_corner

        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If all moves blocked, stay put (engine will keep in place).
    return [int(best_move[0]), int(best_move[1])]