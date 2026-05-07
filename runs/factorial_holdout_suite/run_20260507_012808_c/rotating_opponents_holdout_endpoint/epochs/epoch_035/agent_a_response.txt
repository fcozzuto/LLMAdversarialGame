def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Score resources by denial-first: prefer where opponent is farther (or equal),
    # but ensure we still move toward something if we're behind.
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Primary: maximize opponent advantage over ours (d_op - d_me).
        # Secondary: smaller our distance. Tertiary: further from opponent to reduce race collisions.
        key = (d_op - d_me, -d_op, -d_me)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dist = cheb(nx, ny, tx, ty)
                # Discourage drifting toward where opponent might instantly collect.
                opp_dist = cheb(nx, ny, tx, ty)  # same target; keep deterministic
                # Prefer moves that reduce our distance; slight penalty if move doesn't help.
                moves.append((dist, abs(dx) + abs(dy) == 0, -opp_dist, nx, ny))
    if not moves:
        return [0, 0]

    moves.sort()
    _, _, _, nx, ny = moves[0]
    return [nx - sx, ny - sy]