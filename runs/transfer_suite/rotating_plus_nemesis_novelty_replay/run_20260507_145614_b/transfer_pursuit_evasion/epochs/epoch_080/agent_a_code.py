def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("tag" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def min_obst_d2(x, y):
        md = 10**9
        for bx, by in obst:
            d = dist2(x, y, bx, by)
            if d < md:
                md = d
                if md == 0:
                    return 0
        return 0 if md == 10**9 else md

    target_x, target_y = ox, oy
    best = None
    # Scoring: pursuer minimize distance; evader maximize distance.
    # Keep away from obstacles in both roles.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        d2 = dist2(nx, ny, target_x, target_y)
        od2 = min_obst_d2(nx, ny)
        center_bias = -(dist2(nx, ny, w // 2, h // 2)) * 1e-4  # small, deterministic
        if is_pursuer:
            score = (-d2) + (od2 * 1e-2) + center_bias
            # Prefer immediate capture (d2==0) strongly
            if d2 == 0:
                score += 1e6
        else:
            score = (d2) + (od2 * 1e-2) + center_bias
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]