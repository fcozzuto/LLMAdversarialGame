def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + dy

    # Select a target: prefer resources where we are closer than opponent (or less behind).
    if resources:
        best = None
        best_key = None
        for tx, ty in resources:
            md = dist((sx, sy), (tx, ty))
            od = dist((ox, oy), (tx, ty))
            # key: minimize behind, then my distance, then lexicographic
            key = (md - od, md, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
    else:
        tx, ty = (ox, oy)  # no resources: just move away a bit

    # Choose move by local scoring towards target, avoid opponent, and avoid getting stuck.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = dist((nx, ny), (tx, ty))
        oppd = dist((nx, ny), (ox, oy))
        # If next to opponent, avoid unless it also improves target substantially.
        toward = -myd
        avoid_opp = 0
        if oppd <= 1:
            avoid_opp = -6
        elif oppd == 2:
            avoid_opp = -2
        # Mild preference to keep mobility (prefer squares with more legal moves).
        mob = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay):
                mob += 1
        # If opponent is closer to target, still try to reduce their distance by contesting, but don't suicide.
        contest = 0
        if resources:
            contest = (dist((ox, oy), (tx, ty)) - dist((nx, ny), (tx, ty)))
        score = (toward + avoid_opp) * 10 + contest + mob
        key = (-(score), dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]