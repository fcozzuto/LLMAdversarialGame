def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("tag" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Favor routes that avoid "tight" areas near obstacles and use simple direction targets.
    def obstacle_risk(x, y):
        if (x, y) in obst:
            return 10**7
        r = 0
        for bx, by in obst:
            d = abs(x - bx) + abs(y - by)
            if d == 0:
                r += 10**6
            elif d == 1:
                r += 400
            elif d == 2:
                r += 80
            elif d == 3:
                r += 20
        return r

    best_move = [0, 0]
    best_val = None

    # If pursuer: head toward a "shadow" point slightly beyond evader in the evader's direction.
    # If evader: head to the farthest corner from pursuer (with obstacle-aware penalties).
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    if is_pursuer:
        # Use evader's quadrant as a proxy "direction"
        tx = ox + (1 if ox < (w - 1) / 2 else -1)
        ty = oy + (1 if oy < (h - 1) / 2 else -1)
        tx = max(0, min(w - 1, tx))
        ty = max(0, min(h - 1, ty))
        target = (tx, ty)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            # Encourage decreasing distance to shadow point; keep some direct approach to actual evader too.
            val = -(dist2(nx, ny, target[0], target[1]) * 1.2 + dist2(nx, ny, ox, oy))
            val -= obstacle_risk(nx, ny) * 0.01
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # Evader: go to farthest corner; break ties by preferring larger distance from pursuer and safer obstacle margin.
        target = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            # Primary: maximize distance from pursuer; Secondary: move toward target corner (to reduce chance of corner squeeze).
            val = dist2(nx, ny, ox, oy) * 2.0 + (-(dist2(nx, ny, target[0], target[1])) * 0.12)
            val -= obstacle_risk(nx, ny) * 1.0
            # Slight deterministic bias to stay if equally good
            if (dx, dy) == (0, 0):
                val += 0.001
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]