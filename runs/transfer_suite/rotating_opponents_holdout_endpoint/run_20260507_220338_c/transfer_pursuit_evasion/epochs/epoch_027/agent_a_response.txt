def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("evader" in role)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    target = far_corner if is_evader else (ox, oy)

    def open_neighbors(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                cnt += 1
        return cnt

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_op = dist2(nx, ny, ox, oy)
        d_t = dist2(nx, ny, target[0], target[1])
        open_cnt = open_neighbors(nx, ny)

        if is_evader:
            score = (d_op, open_cnt, -d_t)
        else:
            score = (-d_op, open_cnt, -d_t)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]