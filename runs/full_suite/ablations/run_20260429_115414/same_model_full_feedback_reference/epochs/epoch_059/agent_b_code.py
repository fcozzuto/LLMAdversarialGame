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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    best_move = (0, 0)
    best_score = None

    # Prefer moves that maximize opponent-margins (opponent closer => more positive)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            continue

        local_best = -10**9
        local_dist = 10**9
        local_resource = (nx, ny)

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # larger means we are relatively closer (or opponent farther)
            # Encourage immediate/near capture; also prefer resources that are not currently too close to opponent
            # via opd in tie-breaks.
            score = adv * 100 - myd
            if score > local_best:
                local_best = score
                local_dist = myd
                local_resource = (rx, ry)
            elif score == local_best:
                if myd < local_dist:
                    local_dist = myd
                    local_resource = (rx, ry)

        # Tie-break deterministically: prefer nearer to chosen target, then nearer to center
        tr = local_resource
        center_bias = abs(nx - cx) + abs(ny - cy)
        candidate = (local_best, -local_dist, -center_bias, tr[0], tr[1], dx, dy)
        if best_score is None or candidate > best_score:
            best_score = candidate
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]