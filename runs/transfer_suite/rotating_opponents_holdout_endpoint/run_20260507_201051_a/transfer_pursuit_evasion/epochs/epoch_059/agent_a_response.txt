def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in self_role) and ("evad" not in self_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def step(dx, dy): return sx + dx, sy + dy
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def penalty(x, y):
        if (x, y) in obstacles:
            return 10_000
        best = 999
        for px, py in obstacles:
            d = abs(x - px) + abs(y - py)
            if d < best: best = d
        if best == 0: return 10_000
        if best == 1: return 120
        if best == 2: return 25
        return 0

    # Simple deterministic "zigzag" prediction for pursuer: mirror across self in alternate parity.
    t = int(observation.get("turn_index", 0) or 0)
    if is_pursuer:
        if t % 2 == 0:
            tx = 2 * sx - ox
            ty = 2 * sy - oy
        else:
            tx = 2 * ox - sx
            ty = 2 * oy - sy
        tx = max(0, min(w - 1, tx))
        ty = max(0, min(h - 1, ty))
    else:
        # Evader: choose between two far corners based on parity; avoids "chasing" center.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        c0 = corners[t % 4]
        c1 = corners[(t + 2) % 4]
        tx, ty = (c0 if manh(c0[0], c0[1], ox, oy) > manh(c1[0], c1[1], ox, oy) else c1)

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = step(dx, dy)
        if not inb(nx, ny):
            continue
        p = penalty(nx, ny)
        if p >= 10_000:
            continue
        d_to_target = manh(nx, ny, tx, ty)
        d_to_opp = manh(nx, ny, ox, oy)

        # Pursuer: minimize distance to predicted target and also to opponent.
        # Evader: maximize distance from opponent while also favoring target corner.
        score = (d_to_target * 3 + (0 if is_pursuer else -d_to_opp)) if is_pursuer else (-d_to_opp * 4 + d_to_target)
        score += p

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move