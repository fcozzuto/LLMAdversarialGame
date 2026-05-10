def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or ("evad" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy)) if self_is_evader else None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = [0, 0]
    best_score = None

    order = []
    for dx, dy in moves:
        order.append((dx, dy))
    # Deterministic tie-break preference: straight/diagonal towards/away then lower dx/dy
    order.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d = cheb(nx, ny, ox, oy)
        m = man(nx, ny, ox, oy)

        if self_is_evader:
            to_target = man(nx, ny, target[0], target[1])
            center = abs(nx - cx) + abs(ny - cy)
            score = (d * 10.0) - (to_target * 0.6) - (center * 0.05)
        else:
            center = abs(nx - cx) + abs(ny - cy)
            score = (-d * 10.0) - (m * 0.7) - (center * 0.02)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move in [[-1, -1],[0, -1],[1, -1],[-1,0],[0,0],[1,0],[-1,1],[0,1],[1,1]] else [0, 0]