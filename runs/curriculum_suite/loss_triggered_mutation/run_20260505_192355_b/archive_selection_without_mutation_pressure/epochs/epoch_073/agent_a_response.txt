def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [7, 7])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Pick a target that we are meaningfully closer to than the opponent; otherwise pick nearest overall.
    best_target = resources[0]
    best_key = (-10**9, 10**9, 10**9)
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (od - sd, -sd, od)  # maximize advantage, then prefer smaller sd
        if key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0)
    best_move_score = (-10**18, -10**18)

    # Evaluate each legal move: progress to target, plus deny opponent, plus avoid moving into "bad" cells.
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sd_next = dist(nx, ny, tx, ty)
        od_next = dist(ox, oy, tx, ty)

        # If opponent is close to the target, prioritize increasing their distance from our current move choice.
        # Use a proxy: move that increases our advantage at next step (od - sd_next).
        adv_next = (od_next - sd_next)

        # Safety: penalize being adjacent (8-neighborhood) to obstacles (encourages cleaner lanes vs edge patrol).
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    adj_pen += 1

        # Deterministic tie-break: prefer diagonal slightly if same score, then lowest dx,dy lexicographically.
        score1 = adv_next * 1000 - sd_next - adj_pen * 3
        score2 = -sd_next
        if (score1, score2) > best_move_score or ((score1, score2) == best_move_score and (dx, dy) < best_move):
            best_move_score = (score1, score2)
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]