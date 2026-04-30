def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # drift to center to avoid corner traps
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                d = cheb((nx, ny), (cx, cy))
                if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                    best = (d, (dx, dy))
        return best[1] if best else [0, 0]

    ox, oy = int(op[0]), int(op[1])
    opp_next_target_safe = []
    target = None
    best_key = None

    for r in resources:
        d_me = cheb((sx, sy), r)
        d_op = cheb((ox, oy), r)
        # Prefer resources we can reach strictly not much later than opponent.
        # Large penalty when opponent is closer by 2+.
        delta = d_me - d_op
        penalty = 0
        if delta > 1:
            penalty = (delta - 1) * 10
        # Also prefer resources on our side (agent_b starts at bottom-right).
        side_bonus = 0
        if r[0] <= w // 2:
            side_bonus = -1
        if r[1] <= h // 2:
            side_bonus = -1
        # Key: minimize adjusted distance + beating advantage + penalty.
        key = (d_me + penalty - side_bonus, d_op, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            target = r

    # Move one step toward target; if tie, pick move that also increases our lead vs opponent
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_me_next = cheb((nx, ny), target)
        d_op_now = cheb((ox, oy), target)
        lead = (d_op_now - d_me_next)  # higher is better
        # Secondary: discourage moving away from target.
        away = cheb((sx, sy), target) - d_me_next
        key = (-lead, d_me_next, -away, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return best[1] if best else [0, 0]