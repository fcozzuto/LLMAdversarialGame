def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role) or ("defender" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def neighbors_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                c += 1
        return c

    def edge_penalty(x, y):
        # discourage hugging edges only when evading (to avoid corner trapping); keep light for pursuer
        pen = 0
        if x == 0 or x == w - 1:
            pen += 1
        if y == 0 or y == h - 1:
            pen += 1
        return pen

    best = None
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        md = abs(nx - ox) + abs(ny - oy)  # Manhattan
        cx = abs(nx - (w - 1 if ox < w - 1 else 0)) + abs(ny - (h - 1 if oy < h - 1 else 0))
        free = neighbors_count(nx, ny)

        if is_evader:
            # Maximize distance from pursuer; prefer safer mobility and avoid dead corners.
            # Also bias away from the nearest corner to the pursuer.
            nearest_corner_dist = min(abs(0 - ox) + abs(0 - oy),
                                       abs(0 - ox) + abs((h - 1) - oy),
                                       abs((w - 1) - ox) + abs(0 - oy),
                                       abs((w - 1) - ox) + abs((h - 1) - oy))
            score = (-md, nearest_corner_dist, -edge_penalty(nx, ny), -free)
            # Convert to a comparable key for min()
            key = (score[0], -score[1], score[2], score[3])
        else:
            # Minimize distance; if tied, keep mobility and avoid edge hugging.
            score = (md, edge_penalty(nx, ny), -free, cx)
            key = (score[0], score[1], score[2], score[3])

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]