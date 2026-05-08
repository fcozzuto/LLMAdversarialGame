def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        capture = (nx == ox and ny == oy)
        mobility = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                mobility += 1

        d = dist2(nx, ny)
        if is_evader:
            val = (d * 10.0) + (mobility * 0.2) - (3.0 if capture else 0.0)
        else:
            val = (-d * 10.0) + (mobility * 0.2) + (100000.0 if capture else 0.0)

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best, best_val = (dx, dy), val

    return [best[0], best[1]] if best is not None else [0, 0]