def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    role = (observation.get("self_role") or "").lower()
    is_pursuer = any(k in role for k in ("purs", "hunt", "chaser", "seeker", "hunter", "pursuer", "catch"))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    if not is_pursuer:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        # Pick corner farthest from opponent; tie-break by lexicographic for determinism
        corners.sort()
        target = max(corners, key=lambda c: (dist2(c[0], c[1], ox, oy), -c[0], -c[1]))
    else:
        target = (ox, oy)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_op = dist2(nx, ny, ox, oy)
        d_to_target = dist2(nx, ny, target[0], target[1])
        pen = obst_adj_pen(nx, ny)
        # Deterministic composite score; higher is better
        if is_pursuer:
            score = (-d_to_op) * 10 + (-d_to_target) + (-pen) * 0.5
        else:
            score = (d_to_op) * 10 + (-d_to_target) + (-pen) * 0.5
        if best is None or score > best:
            best = score
            best_move = [dx, dy]
    return best_move