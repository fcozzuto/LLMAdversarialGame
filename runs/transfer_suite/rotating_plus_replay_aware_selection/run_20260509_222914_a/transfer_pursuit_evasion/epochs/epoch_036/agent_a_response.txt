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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy)) if is_evader else \
                     min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def obst_penalty(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best <= 1:
            return 50
        return 5.0 / (best + 1)

    # Also discourage becoming adjacent to opponent when evading; encourage when pursuing.
    def score(x, y):
        d = (abs(x - ox) + abs(y - oy))
        toward_corner = abs(x - target_corner[0]) + abs(y - target_corner[1])
        if is_evader:
            # Prefer larger distance from opponent and smaller distance to chosen corner.
            return (10.0 * d) - toward_corner - obst_penalty(x, y)
        else:
            # Pursuer: minimize distance to opponent and avoid obstacles; prefer cutting toward evader's corner.
            return (-10.0 * d) - obst_penalty(x, y) - 0.1 * toward_corner

    best_s = None
    best = (0, 0)
    # Deterministic tie-break: fixed move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        sc = score(nx, ny)
        if best_s is None or sc > best_s:
            best_s = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]