def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Target selection: race advantage (opponent far from target while we are close).
    target = None
    best_adv = None
    for rx, ry in resources:
        selfd = dist2(sx, sy, rx, ry)
        oppd = dist2(ox, oy, rx, ry)
        adv = oppd - selfd  # higher is better
        if best_adv is None or adv > best_adv or (adv == best_adv and (rx, ry) < target):
            best_adv = adv
            target = (rx, ry)

    if target is None:
        # No visible resources: head toward center while keeping some distance from opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)

    rx, ry = target
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer decreasing distance to target; avoid dead-ends; also keep away from opponent.
        d_to = dist2(nx, ny, rx, ry)
        d_op = dist2(nx, ny, ox, oy)
        neigh = 0
        for ddx, ddy in moves:
            xx, yy = nx + ddx, ny + ddy
            if valid(xx, yy):
                neigh += 1
        score = (d_to * 10) - (d_op // 2) - neigh
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]