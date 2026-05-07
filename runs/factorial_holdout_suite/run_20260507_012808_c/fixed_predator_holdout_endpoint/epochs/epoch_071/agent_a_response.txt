def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    tr = int(observation.get("turns_remaining", 0) or 0)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def cd(a, b):
        ax, ay = a
        bx, by = b
        da = abs(ax - bx)
        db = abs(ay - by)
        return da if da >= db else db

    best = None
    best_key = None
    for dx, dy in valid:
        ns = (sx + dx, sy + dy)
        best_res_key = None
        for rx, ry in resources:
            r = (rx, ry)
            self_d = cd(ns, r)
            opp_d = cd((ox, oy), r)
            margin = opp_d - self_d
            # Encourage winning closer resources and reaching before time runs out
            time_bonus = 0
            if tr > 0:
                time_bonus = 0.5 if self_d <= tr and opp_d > self_d else (-0.25 if opp_d < self_d else 0)
            # Prefer higher margin; if tied, prefer closer self
            key = (margin + time_bonus, -self_d, rx + ry)
            if best_res_key is None or key > best_res_key:
                best_res_key = key
        # If multiple moves lead to similar best resource margin, keep closer to it
        move_key = (best_res_key[0], best_res_key[1], best_res_key[2])
        if best_key is None or move_key > best_key:
            best_key = move_key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]