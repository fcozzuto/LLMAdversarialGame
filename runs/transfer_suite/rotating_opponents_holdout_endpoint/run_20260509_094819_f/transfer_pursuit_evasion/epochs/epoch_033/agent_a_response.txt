def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    role = (observation.get("self_role", "") or "").lower()
    env = (observation.get("environment_name", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("evasion" in role) or ("evad" in env) or ("escape" in env) or ("evasion" in env)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if inb(x + dx, y + dy):
                c += 1
        return c

    # Deterministic target selection
    if is_evader:
        # Prefer running toward the farthest corner from pursuer (corner heuristic).
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        tx, ty = ox, oy

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        # If evader: maximize distance from opponent, also reduce distance to chosen corner.
        # If pursuer: minimize distance to opponent, also prefer higher mobility to avoid trapping into obstacles.
        if is_evader:
            score = (d_to_opp, -d_to_target, mob, -dx, -dy)
            better = (best_score is None) or (score > best_score)
        else:
            score = (-d_to_opp, d_to_target, mob, -dx, -dy)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]