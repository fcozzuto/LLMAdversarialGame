def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in self_role) or ("tag" in self_role) or ("hunter" in self_role)
    if not pursuer and (("purs" in opp_role) or ("tag" in opp_role) or ("hunter" in opp_role)):
        pursuer = False

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_center = dist2(nx, ny, cx, cy)
        # Pursuer: minimize distance to opponent and avoid edge/leap-through when possible.
        # Evader: maximize distance to opponent while preferring central maneuvering.
        if pursuer:
            score = -d_opp + 0.01 * d_center
        else:
            score = d_opp - 0.005 * d_center
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move