def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    center = (w // 2, h // 2)
    if not resources:
        tx, ty = center
    else:
        # Prefer resources where we're closer than opponent; otherwise deny opponent's closest.
        best = None
        best_key = None
        for rx, ry in resources:
            our_d = cheb(sx, sy, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            adv = op_d - our_d  # positive means we have a pull
            # Key: maximize advantage; then minimize our distance; then lexicographic
            key = (adv, -our_d, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        d_self_now = cheb(sx, sy, tx, ty)
        # Move toward target, but keep away from opponent; also reward if we improve over current distance.
        val = (-d_self) + 0.25 * d_opp + 0.6 * (d_self_now - d_self)
        # Small tie-break: prefer moves that reduce max coordinate change to stabilize.
        val += -0.01 * (abs(dx) + abs(dy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]