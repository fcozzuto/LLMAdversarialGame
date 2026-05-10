def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("pursuit" in role)

    # If role name ambiguous, infer by relative scoring: pursuer typically scores on capture; evader otherwise.
    if not is_pursuer:
        is_pursuer = ("evader" not in role)  # default to pursuer in ambiguous cases

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = corners[(observation.get("turn_index", 0) or 0) % 4]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)

        # Obstacle proximity penalty/bonus to reduce oscillations.
        obs_pen = 0
        for (bx, by) in blocked:
            t = man(nx, ny, bx, by)
            if t == 0:
                obs_pen = 999
                break
            if t == 1:
                obs_pen += 1
        if obs_pen >= 999:
            continue

        if is_pursuer:
            # Prefer minimizing distance to opponent; when tied, bias toward opponent's side.
            score = d_opp * 1000 + obs_pen * 10 + man(nx, ny, ox, oy)  # redundant but deterministic
        else:
            # Evader: maximize distance from opponent; also drift toward a corner that is farther.
            corner_bias = man(target_corner[0], target_corner[1], ox, oy)  # constant-like
            score = -d_opp * 1000 + obs_pen * 10 - corner_bias + man(nx, ny, target_corner[0], target_corner[1])

        key = (score, dx, dy, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]