def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    self_role = observation.get("self_role", "") or ""
    role = self_role.lower()

    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            try:
                obs.add((int(b[0]), int(b[1])))
            except:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def near_block_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if blocked(x + dx, y + dy):
                    p += 1
        return p

    actions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break: fixed action ordering.
    best_a = actions[4]
    best_v = None

    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if blocked(nx, ny):
            nx, ny = sx, sy

        d = dist2(nx, ny, ox, oy)
        p = near_block_pen(nx, ny)

        if "evader" in role:
            # Maximize distance from pursuer.
            v = d - 0.35 * p
            better = (best_v is None) or (v > best_v)
        else:
            # Pursuer: minimize distance.
            v = -d - 0.35 * p
            better = (best_v is None) or (v > best_v)

        if better:
            best_v = v
            best_a = (dx, dy)

    return [int(best_a[0]), int(best_a[1])]