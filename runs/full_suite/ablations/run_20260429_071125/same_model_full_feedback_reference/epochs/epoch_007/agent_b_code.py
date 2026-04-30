def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obs or not resources:
        return [0, 0]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource with a simple deterministic tie-break.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = manhattan(sx, sy, rx, ry)
        od = manhattan(ox, oy, rx, ry)
        key = (sd - od * 0.3, sd, od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd_next = manhattan(nx, ny, tx, ty)
        sd_now = manhattan(sx, sy, tx, ty)
        opp_next = manhattan(nx, ny, ox, oy)

        # If opponent is closer to the target, prefer moves that increase distance to opponent.
        opp_closer = manhattan(ox, oy, tx, ty) < sd_now
        score = (sd_next, opp_next if opp_closer else -opp_next)

        # Prefer improving toward target; break ties deterministically by dx,dy.
        key = (score[0], score[1], abs(dx), dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move