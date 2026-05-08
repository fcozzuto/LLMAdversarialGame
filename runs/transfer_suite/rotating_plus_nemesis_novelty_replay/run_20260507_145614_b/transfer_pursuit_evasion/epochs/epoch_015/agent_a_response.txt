def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("pursuer" not in self_role and "pursuer" in opp_role) or (self_role == "")

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    target = far_corner if is_evader else near_corner

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, target[0], target[1])
        # Evader: maximize distance from pursuer and drift toward far corner
        # Pursuer: minimize distance to evader and drift toward near corner
        val = (d_opp * 5 + (-d_tgt)) if is_evader else ((-d_opp) * 5 + (-d_tgt))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]