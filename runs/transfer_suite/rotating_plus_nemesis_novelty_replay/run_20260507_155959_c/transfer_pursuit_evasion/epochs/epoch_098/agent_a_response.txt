def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader")
    pursue = (not self_evader) or opp_evader

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        if nx == ox and ny == oy:
            return [dx, dy]

        d2 = dist2(nx, ny, ox, oy)
        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        # Pursuer: minimize distance; Evader: maximize distance and prefer being away from edges.
        val = (-d2 if pursue else d2) + (0.08 * edge if not pursue else -0.02 * edge)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move