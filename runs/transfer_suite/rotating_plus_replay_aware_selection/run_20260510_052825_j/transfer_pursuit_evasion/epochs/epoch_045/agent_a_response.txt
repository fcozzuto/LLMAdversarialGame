def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)
    # self_is_pursuer = not self_is_evader (roles may be missing)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1), (0, 0)]

    best_move = [0, 0]
    best_val = None

    # Deterministic tie-break: prefer diagonal, then orthogonal, then stay (already ordered in deltas)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d = man(nx, ny, ox, oy)
        # If pursuer: minimize distance; if evader: maximize distance.
        if self_is_evader:
            val = (d, -man(nx, ny, 0, 0), -man(nx, ny, w - 1, h - 1))
        else:
            val = (-d, man(nx, ny, 0, 0), man(nx, ny, w - 1, h - 1))

        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]