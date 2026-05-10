def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    candidates = []
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (sx, sy):
            path_bonus = 0
        else:
            path_bonus = 1  # prefer actual movement when possible

        best_val = -10**18
        # evaluate move by what resource we can "secure" next (closer than opponent)
        for rx, ry in resources:
            r = (rx, ry)
            d_self = dist((nx, ny), r)
            d_opp = dist((ox, oy), r)
            # Secure if we're strictly closer; otherwise deprioritize.
            secure_margin = d_opp - d_self
            val = secure_margin * 10 - d_self
            # tie-break toward nearer resources and those farther from opponent when not secure
            if secure_margin <= 0:
                val -= (d_self * 2) + (0 if d_opp == d_self else (d_opp - d_self))
            # slight preference for moving closer to any resource to avoid stalling
            val += path_bonus
            # deterministic secondary ordering
            val += - (rx * 0.001 + ry * 0.0001)
            if val > best_val:
                best_val = val
        candidates.append((best_val, dx, dy))

    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]