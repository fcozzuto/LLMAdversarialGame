def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        moves = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]
        bx = 1 if sx < w - 1 else (-1 if sx > 0 else 0)
        by = 1 if sy < h - 1 else (-1 if sy > 0 else 0)
        return [bx, by]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Choose targets that we can reach first (or at least not lose badly).
    # Score move by worst-case loss and proximity to promising targets.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        move_score = 0
        # Evaluate a few most relevant resources deterministically.
        # Sort by my distance, tie by coordinate to keep determinism.
        scored = sorted(resources, key=lambda r: (cheb(nx, ny, r[0], r[1]), r[0], r[1]))
        for i, (rx, ry) in enumerate(scored[:6]):
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer states where I am closer than opponent, but keep pressure on others.
            gain = (opd - myd)  # positive is good
            # Extra reward for being able to grab soon; extra penalty if opponent is very close.
            move_score += 20 * gain - 3 * myd - (0 if opd - myd >= 0 else 8 * (-(opd - myd)))
            # Small preference to reduce distance monotically
            move_score -= 0.5 * cheb(sx, sy, rx, ry)
            if i == 0:
                move_score += 5  # focus the best candidate
        # Mild preference for staying away from being corner-trapped by obstacles:
        # prefer moves that have at least one inside neighbor (including staying).
        neigh_ok = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inside(tx, ty):
                neigh_ok += 1
        move_score += 0.2 * neigh_ok
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]