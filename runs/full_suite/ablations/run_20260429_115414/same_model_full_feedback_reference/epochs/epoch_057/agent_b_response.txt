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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource that we can reach earlier (or better advantage).
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer: bigger advantage (opd - myd), then smaller my distance, then nearer upper-left deterministically.
        key = (opd - myd, -myd, -(rx + 17 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    # Deterministic tie-breaker order by iteration order; scores decide.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obstacles:
            continue

        myd = cheb(nx, ny, tx, ty)
        # Opponent potential: estimate their advantage if we move here.
        opd = cheb(ox, oy, tx, ty)
        # Encourage: go closer to target, keep/extend advantage, and prefer staying away from obstacles via simple local penalty.
        obs_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if 0 <= px < W and 0 <= py < H and (px, py) in obstacles:
                    obs_pen += 1
        score = (opd - myd, -myd, -obs_pen, -(nx + 13 * ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]