def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    self_role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in self_role
    # If role names are odd, infer: evader -> maximize distance, otherwise pursue.
    if not is_evader and ("pursuer" in self_role):
        is_evader = False
    if not is_evader and "evader" not in self_role:
        # default: if not explicitly evader, assume pursuer
        is_evader = False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obst_near(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obst:
                    c += 1
        return c

    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        md = abs(nx - ox) + abs(ny - oy)

        if is_evader:
            # Prefer maximizing distance, but avoid getting boxed in near walls/obstacles.
            near = obst_near(nx, ny)
            key = (d, -md, -near, -dx == 0 and -dy == 0)
            better = best is None or key > best
        else:
            # Prefer minimizing distance; tie-break to reduce approach error and avoid obstacle adjacency.
            near = obst_near(nx, ny)
            key = (-d, md, near, dx == 0 and dy == 0)
            better = best is None or key > best

        if better:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]