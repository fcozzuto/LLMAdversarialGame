def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or (self_role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return (abs(x1 - x2) + abs(y1 - y2))

    best = None
    # Tie-break preference order: favor larger x then larger y deterministically.
    # Score: evader maximize; pursuer minimize; both prefer fewer "bad" moves near obstacles.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist(nx, ny, ox, oy)
        # obstacle pressure: penalize proximity to obstacles to avoid getting wedged
        obst_pen = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                ax, ay = nx + adx, ny + ady
                if (ax, ay) in obstacles:
                    obst_pen += 1
        if is_evader:
            score = (d * 10) - obst_pen
            key = (score, nx, ny)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        else:
            score = (-d * 10) + (-obst_pen)
            key = (score, nx, ny)
            if best is None or key > best[0]:
                best = (key, [dx, dy])

    if best is None:
        # All moves invalid: stay
        return [0, 0]
    return best[1]