def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    ob = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in role

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in ob

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic corner bias: evader heads to farthest corner from opponent; pursuer heads to closest.
    best_corner = corners[0]
    best_key = None
    for cx, cy in corners:
        d_op = manh(cx, cy, ox, oy)
        if self_is_evader:
            key = (d_op, -manh(cx, cy, sx, sy), cx, cy)  # far from opponent, also somewhat toward me to reduce dithering
        else:
            key = (-d_op, manh(cx, cy, sx, sy), cx, cy)  # near opponent's likely region
        if best_key is None or key > best_key:
            best_key, best_corner = key, (cx, cy)

    cx, cy = best_corner
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op_next = manh(nx, ny, ox, oy)
        d_corner_next = manh(nx, ny, cx, cy)
        if self_is_evader:
            # maximize distance from pursuer; slight preference to reach corner
            score = (d_op_next, -d_corner_next, dx, dy)
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)
        else:
            # minimize distance to evader; help cut them off toward the biased corner
            score = (-d_op_next, -d_corner_next, dx, dy)
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]