def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obst_pen(x, y):
        if not obstacles:
            return 0.0
        dmin = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < dmin:
                dmin = d
        if dmin == 0:
            return 1e6
        if dmin <= 1:
            return 200.0
        return 5.0 / (dmin + 1)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in obstacles:
            continue
        # If invalid/out of bounds, staying is enforced by engine; keep deterministic by allowing it with penalty.
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dist = abs(nx - ox) + abs(ny - oy)
        if is_evader:
            # Maximize distance; bias toward corners to avoid cycles.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_dist = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            val = dist * 10.0 + corner_dist - obst_pen(nx, ny) * 2.0
        else:
            # Minimize distance; encourage progress and avoid obstacle zones.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_seek = min(abs(ox - cx) + abs(oy - cy) for cx, cy in corners)
            val = -dist * 10.0 - obst_pen(nx, ny) * 2.0 - corner_seek * 0.01
        # Deterministic tie-break: smaller dx, then smaller dy.
        if best is None or val > best or (val == best and (dx, dy) < tuple(best_move)):
            best = val
            best_move = [dx, dy]

    return best_move