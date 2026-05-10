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

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        cheb = max(abs(nx - ox), abs(ny - oy))
        # Pursuer: minimize distance; Evader: maximize distance
        primary = cheb if not self_is_pursuer else -cheb

        # Tie-breakers: avoid getting stuck near borders; steer by center drift
        border = min(nx, w - 1 - nx, ny, h - 1 - ny)
        border_term = border if not self_is_pursuer else -border

        center_dist = abs(nx - cx) + abs(ny - cy)
        center_term = center_dist if not self_is_pursuer else -center_dist

        # Deterministic ordering
        tie = (dx, dy)

        key = (primary, border_term, center_term, tie)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]