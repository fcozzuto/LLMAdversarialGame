def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corners_sorted = sorted(corners, key=lambda c: dist2(c[0], c[1], ox, oy), reverse=self_is_evader)
    # If evader, move toward farthest-from-opponent corner; if pursuer, move toward opponent.
    if self_is_evader:
        tx, ty = corners_sorted[0]
        score_sign = 1
    else:
        tx, ty = ox, oy
        score_sign = -1

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Composite score:
        # - If pursuer: minimize distance to opponent; small bias toward aligning with opponent-corner axis.
        # - If evader: maximize distance to opponent; small bias toward target corner.
        d_op = dist2(nx, ny, ox, oy)
        d_t = dist2(nx, ny, tx, ty)
        if self_is_evader:
            sc = score_sign * d_op - (d_t * 0.01)
        else:
            # Prefer reducing d_op strongly, then reduce d_t slightly (when tx is opponent it's consistent).
            sc = (d_op * 1.0) + (d_t * 0.01)
        if best is None:
            best = sc
            best_move = (dx, dy)
        else:
            if self_is_evader:
                if sc > best:
                    best, best_move = sc, (dx, dy)
            else:
                if sc < best:
                    best, best_move = sc, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]