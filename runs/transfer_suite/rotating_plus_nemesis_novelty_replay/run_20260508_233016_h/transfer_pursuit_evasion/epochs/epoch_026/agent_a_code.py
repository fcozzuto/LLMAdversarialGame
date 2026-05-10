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

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in self_role) or ("tag" in self_role) or ("hunter" in self_role)
    if not pursuer and (("purs" in opp_role) or ("tag" in opp_role) or ("hunter" in opp_role)):
        pursuer = False

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_to_opp = dist2(nx, ny, ox, oy)

        # Secondary terms: prefer approaching/corner-clamping and avoiding edges when beneficial.
        # For pursuer: approach opponent, and prefer keeping opponent in "toward-center" direction.
        # For evader: maximize distance and prefer toward opposite corner.
        center_pen = dist2(nx, ny, cx, cy) * 0.001
        opp_center_pen = dist2(ox, oy, cx, cy) * 0.001
        if pursuer:
            # clamp/contain: moving so that opponent is "farther from center" after our move is good for capture
            contain_term = dist2(ox, oy, cx, cy) - dist2(nx, ny, cx, cy)
            key = (d_to_opp, -contain_term, center_pen)
        else:
            # evader: keep separation; bias away from opponent's direction to avoid being mirrored into corner
            contain_term = dist2(nx, ny, cx, cy) - dist2(ox, oy, cx, cy)
            key = (-d_to_opp, contain_term, center_pen)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best