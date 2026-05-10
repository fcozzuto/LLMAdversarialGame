def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)
    self_is_pursuer = ("purs" in self_role) or (self_role == "pursuer")

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Resource not used for pursuit/evasion scoring, but can lightly bias to break ties.
    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if self_is_evader and not self_is_pursuer:
        # Escape toward farthest corner from pursuer.
        tx, ty = max(corners, key=lambda c: man(c[0], c[1], ox, oy))
        want_bigger = True
    else:
        # Pursue toward a point closer to opponent; bias to align with opponent direction.
        tx, ty = ox, oy
        want_bigger = False

    def step_score(x, y):
        if (x, y) in obstacles:
            return -10**9
        d = man(x, y, ox, oy)
        # Choose evasion = maximize distance; pursuit = minimize distance.
        score = d if want_bigger else -d

        # Gentle tie-break: progress toward chosen target.
        dt = man(x, y, tx, ty)
        score += (1 if want_bigger else -1) * (1.5 / (1 + dt))

        # Avoid stepping into opponent's "shadow" when evading.
        if want_bigger:
            dx = 1 if x > ox else (-1 if x < ox else 0)
            dy = 1 if y > oy else (-1 if y < oy else 0)
            shadow = (ox + dx, oy + dy)
            if (x, y) == shadow:
                score -= 1.25

        # Light resource bias only if not empty.
        if res:
            nearest = min(man(x, y, rx, ry) for rx, ry in res)
            score += (0.2 if want_bigger else 0.12) / (1 + nearest)

        return score

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = step_score(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = [dx, dy]
    return best_move