def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    if not inb(sx, sy):
        for dx, dy in dirs:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        # target nearest resource (tie by y then x for determinism)
        best_t = resources[0]
        best_d = abs(best_t[0] - sx) + abs(best_t[1] - sy)
        for x, y in resources[1:]:
            d = abs(x - sx) + abs(y - sy)
            if d < best_d or (d == best_d and (y, x) < (best_t[1], best_t[0])):
                best_d, best_t = d, (x, y)
        tx, ty = best_t

        best_score = None
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = abs(tx - nx) + abs(ty - ny)
            # small preference to move away from opponent if close, otherwise focus on resources
            opp = abs(ox - nx) + abs(oy - ny)
            score = (d, -opp, dx == 0 and dy == 0)
            if best_score is None or score < best_score:
                best_score, best_move = score, [dx, dy]
        return best_move

    # No resources: move toward center, with a slight deterrent from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = abs(cx - nx) + abs(cy - ny)
        opp = abs(ox - nx) + abs(oy - ny)
        score = (d, -opp, dx == 0 and dy == 0)
        if best_score is None or score < best_score:
            best_score, best_move = score, [dx, dy]
    return best_move