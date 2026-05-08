def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = any(k in role for k in ("purs", "hunt", "chaser", "seeker", "hunter", "pursuer", "catch", "catcher"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def obs_pen(nx, ny):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    pen += 3
        if (nx, ny) in obstacles:
            pen += 999
        # Wall penalty: discourages hugging edges when trying to chase (helps against wall runners)
        if is_pursuer:
            if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
                pen += 1
        return pen

    target_first = (observation.get("turn_index", 0) % 2 == 0)

    best = None
    best_score = None
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        pen = obs_pen(nx, ny)
        # Pursuer: minimize distance; Evader: maximize distance.
        base = (-d if is_pursuer else d)
        # Prefer moves that reduce/increase distance along the immediate line to opponent.
        vec_dot = (nx - sx) * (ox - sx) + (ny - sy) * (oy - sy)
        line_term = (1 if is_pursuer else -1) * (vec_dot != 0) * (abs(vec_dot) // 1)
        # Small deterministic tie-breaker: favor a consistent order and direction choice.
        tie = (i % 3) * 0.01
        score = base - pen + (line_term if is_pursuer else -line_term) - tie
        if best_score is None:
            best, best_score = [dx, dy], score
        else:
            better = score > best_score if not target_first else score >= best_score
            if better:
                best, best_score = [dx, dy], score

    if best is None:
        return [0, 0]
    return best