def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = observation.get("self_role", "pursuer")
    is_pursuer = (self_role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    farthest_corner_from_op = None
    best_corner_metric = None
    for cx, cy in corners:
        m = abs(cx - ox) + abs(cy - oy)
        if best_corner_metric is None or m > best_corner_metric:
            best_corner_metric = m
            farthest_corner_from_op = (cx, cy)

    # Evader: primarily run away, secondarily drift toward farthest corner to avoid wall-jukes.
    # Pursuer: primarily chase, secondarily keep pressure toward the evader's side/corner.
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dist_to_op = d2(nx, ny, ox, oy)
        # Obstacle proximity penalty to avoid tight wall-running traps (still deterministic).
        prox = 0
        for ox2, oy2 in obstacles:
            if abs(ox2 - nx) <= 1 and abs(oy2 - ny) <= 1:
                prox += 1

        if is_pursuer:
            ccx, ccy = farthest_corner_from_op
            corner_push = d2(nx, ny, ccx, ccy)
            score = -dist_to_op - 0.25 * corner_push - 0.5 * prox
        else:
            ccx, ccy = farthest_corner_from_op
            corner_pull = d2(nx, ny, ccx, ccy)
            # Prefer larger distance from pursuer; also prefer moves that increase distance to corner-pursuit line.
            score = dist_to_op + 0.35 * corner_pull - 0.75 * prox

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]