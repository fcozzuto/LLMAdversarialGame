def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                sx, sy = sx + dx, sy + dy
                break
        else:
            return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If any reachable move captures a resource, do it.
    res_set = set(resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    center = (w // 2, h // 2)
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Prefer moves that improve advantage toward good targets.
        if resources:
            # Evaluate by best (self advantage) target from this candidate position.
            cand_best = None
            for tx, ty in resources:
                ds = man(nx, ny, tx, ty)
                do = man(ox, oy, tx, ty)
                # higher is better: we want do - ds large, then smaller ds tie-break
                score = (do - ds, -ds, -man(nx, ny, center[0], center[1]))
                cand_best = score if cand_best is None or score > cand_best else cand_best
            score = cand_best
        else:
            # No resources: move toward center deterministically.
            score = (-man(nx, ny, center[0], center[1]),)

        # Deterministic compare with tuple ordering; include move index tie-break.
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If all blocked (shouldn't happen), stay put.
    if best_score is None:
        return [0, 0]
    return best_move