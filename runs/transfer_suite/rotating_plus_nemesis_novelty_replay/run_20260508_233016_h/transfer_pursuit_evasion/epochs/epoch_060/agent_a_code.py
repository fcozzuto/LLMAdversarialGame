def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # If already on opponent (capture radius 0), stay.
    if sx == ox and sy == oy:
        return [0, 0]

    best_move = [0, 0]
    best_worst = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # One-step minimax: opponent chooses move maximizing our distance; we minimize that worst-case.
        worst = -1
        for odx, ody in deltas:
            mx, my = ox + odx, oy + ody
            if not legal(mx, my):
                continue
            d = dist2(nx, ny, mx, my)
            if d > worst:
                worst = d

        if worst == -1:
            worst = dist2(nx, ny, ox, oy)

        # Tie-break: prefer smaller actual distance to opponent after our move.
        actual = dist2(nx, ny, ox, oy)
        key = (worst, actual)
        if best_worst is None or key < best_worst[0:2]:
            best_worst = (worst, actual)
            best_move = [dx, dy]

    return best_move