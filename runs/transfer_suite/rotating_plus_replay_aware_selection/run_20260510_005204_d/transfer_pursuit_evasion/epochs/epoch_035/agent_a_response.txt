def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    # In pursuit_evasion: pursuer catches evader; self should maximize score based on its role
    self_is_pursuer = ("pursuer" in self_role) or ("pursuer" in opp_role and "evader" not in self_role)
    if ("pursuer" not in self_role) and ("evader" not in self_role) and ("pursuer" in opp_role):
        self_is_pursuer = True
    if "evader" in self_role:
        self_is_pursuer = False

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Deterministic preference order: keep closer to opponent direction for pursuer; opposite for evader
    # Tie-breaker uses smaller dx, then smaller dy lexicographically.
    def score(nx, ny):
        dx = abs(nx - ox)
        dy = abs(ny - oy)
        dist = dx if dx > dy else dy  # Chebyshev distance
        # pursuer wants smaller distance; evader wants larger distance
        return dist if not self_is_pursuer else -dist

    best = None
    best_move = [0, 0]
    # Prefer moves that also increase survival by staying away from obstacles adjacency a bit
    obstacle_list = list(blocked)

    def obstacle_penalty(nx, ny):
        pen = 0
        for bx, by in obstacle_list:
            if abs(nx - bx) <= 1 and abs(ny - by) <= 1:
                pen += 1
        return pen

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue
        sc = score(nx, ny)
        # For pursuer: avoid obstacles slightly; for evader: also avoid getting boxed in
        sc -= (obstacle_penalty(nx, ny) * (0.02 if self_is_pursuer else 0.01))
        key = (sc, -abs(dxm), -abs(dym), dxm, dym)  # deterministic
        if best is None or key > best:
            best = key
            best_move = [dxm, dym]

    return best_move