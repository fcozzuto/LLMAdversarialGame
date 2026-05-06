def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        cand_targets = sorted(resources, key=lambda t: (man((sx, sy), t), t[0], t[1]))[:3]
    else:
        cand_targets = [(w // 2, h // 2)]

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer reducing own distance to promising resources while keeping an edge over opponent.
        # Also lightly discourage moving onto squares close to opponent (to reduce contest).
        score = 0
        for t in cand_targets:
            ds_self = man((nx, ny), t)
            ds_opp = man((ox, oy), t)
            score += (ds_opp - ds_self)
        score = score - 0.15 * man((nx, ny), (ox, oy))

        # If all else ties, prefer moves that make progress roughly toward the nearest target.
        if resources:
            nt = cand_targets[0]
            score += -0.01 * man((nx, ny), nt)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]