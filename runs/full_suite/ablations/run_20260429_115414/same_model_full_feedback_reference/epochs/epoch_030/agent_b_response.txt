def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        tx = (W - 1) // 2
        ty = (H - 1) // 2
        if (tx, ty) in obs:
            tx, ty = (sx, sy)
        resources = [(tx, ty)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Choose a target we are at least as close to (in Manhattan), and otherwise deny by best advantage.
    best_t = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Prefer resources where ds <= do; otherwise still pick those where we reduce the gap most.
        key = (1 if ds <= do else 0, (ds - do), ds + do)
        # Higher ds-do is worse; using tuple with first element as above then minimizing remaining.
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t

    moves = []
    for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            moves.append((dx, dy))

    # Evaluate moves: minimize our distance to target, and maximize our lead versus opponent for that target.
    best_step = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ds_next = md(nx, ny, rx, ry)
        do_now = md(ox, oy, rx, ry)
        # Primary: be closer to target; Secondary: increase (do_now - ds_next); Tertiary: avoid giving opponent advantage (prefer staying away from opponent).
        val = (ds_next, -(do_now - ds_next), md(nx, ny, ox, oy))
        if best_val is None or val < best_val:
            best_val = val
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]