def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    role = str(observation.get("self_role", "pursuer") or "pursuer").lower()
    evade = ("evad" in role) or ("run" in role) or ("away" in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        dx = x - ox
        if dx < 0:
            dx = -dx
        dy = y - oy
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for ax, ay in deltas:
            nx, ny = x + ax, y + ay
            if ok(nx, ny):
                c += 1
        return c

    t = int(observation.get("turn_index", 0) or 0)
    # Deterministic preference: rotate ordering to break ties without randomness
    shift = (t % 9)
    ordered = deltas[shift:] + deltas[:shift]

    best_move = (0, 0)
    best_key = None

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny)
        m = mobility(nx, ny)
        # pursuer: minimize distance; evader: maximize distance
        key = (d, -m) if not evade else (-d, m)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]