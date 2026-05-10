def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    self_role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("tagger" in self_role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = max(abs(nx - ox), abs(ny - oy))
        # pursuer wants smaller distance; evader wants larger distance
        val = (-d if pursuer else d)
        # tiny bias to avoid staying when not needed
        if dx == 0 and dy == 0:
            val -= 0.01
        # tiny bias for staying in bounds already ensured; tie-break by move order
        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    if best is None:
        return [0, 0]
    return best