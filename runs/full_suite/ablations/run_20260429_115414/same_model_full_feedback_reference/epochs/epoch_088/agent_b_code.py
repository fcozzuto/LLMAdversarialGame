def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target where we have a deterministic "material" advantage; else the one we can reach fastest.
    if resources:
        best_adv = None
        best_far = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we're closer/tie
            key_adv = (adv, -sd, rx, ry)  # prefer larger advantage, then smaller sd, then deterministic tie
            if best_adv is None or key_adv > best_adv[0]:
                best_adv = (key_adv, (rx, ry))
            key_far = (-sd, rx, ry)
            if best_far is None or key_far > best_far[0]:
                best_far = (key_far, (rx, ry))
        target = best_adv[1] if best_adv[0][0] > 0 else best_far[1]
    else:
        # No visible resources: move toward the board center deterministically.
        target = (W // 2, H // 2)

    tx, ty = target

    # Step greedily toward target, but break ties by trying to delay opponent's approach to the same target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Score: primarily minimize my distance; then maximize opponent distance (slow them);
        # then deterministic tie by preferring moves that keep heading "up-right" style via (dx,dy).
        score = (myd, -opd, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]