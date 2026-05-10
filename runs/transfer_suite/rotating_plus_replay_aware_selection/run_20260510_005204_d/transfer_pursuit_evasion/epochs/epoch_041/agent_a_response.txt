def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in self_role) or (("pursuer" in opp_role) and ("evader" not in self_role))

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_dx, best_dy = 0, 0
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        cheb = max(abs(nx - ox), abs(ny - oy))
        # primary objective: pursue -> minimize, evade -> maximize
        primary = -cheb if self_is_pursuer else cheb

        # secondary: keep off borders (avoid trapping by obstacles/boundaries)
        dist_border = min(nx, ny, (w - 1 - nx), (h - 1 - ny))
        border_score = dist_border * (1.0 if self_is_pursuer else 0.5)

        # tertiary: drift toward center to improve pursuit geometry / evade escape routes
        center_score = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        # combine deterministically with weights
        score = primary * 10.0 + border_score + center_score * (0.01 if self_is_pursuer else -0.005)

        if best_score is None or score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]