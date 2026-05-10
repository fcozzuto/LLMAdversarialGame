def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    tr = int(observation.get("turns_remaining", 0))
    prefer_feasible = (tr % 2 == 0)

    best = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        feasible = (my_d <= op_d)
        # Primary: beat opponent (or close), Secondary: smaller my distance, Tertiary: deterministic target order
        key = (-(1 if (feasible or not prefer_feasible) else 0), my_d - op_d, my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    # Candidate moves: all deltas in {-1,0,1}^2 including stay
    moves = []
    dx0 = sign(tx - sx)
    dy0 = sign(ty - sy)
    moves.append((dx0, dy0))
    if dx0 != 0:
        moves.append((0, dy0))
        moves.append((dx0, 0))
    if dy0 != 0 and (0, dy0) not in moves:
        moves.append((0, dy0))
    if (dx0, 0) not in moves and dx0 != 0:
        moves.append((dx0, 0))
    # Fill with remaining neighbors deterministically
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not (dx == 0 and dy == 0):
                if (dx, dy) not in moves:
                    moves.append((dx, dy))
    moves.append((0, 0))

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_next = cheb(nx, ny, tx, ty)
        # If we can reach target immediately, do it; otherwise prefer reducing distance and improving relative to opponent.
        op_d = cheb(ox, oy, tx, ty)
        feasible_next = (my_next <= op_d)
        key = (-(1 if feasible_next else 0), my_next, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]