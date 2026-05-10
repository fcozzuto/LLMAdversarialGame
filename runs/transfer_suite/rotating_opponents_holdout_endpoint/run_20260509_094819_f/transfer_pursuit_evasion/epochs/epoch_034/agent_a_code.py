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

    # Greedy one-step evaluation with deterministic tie-breaks
    best = None  # (score, -mob, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        if is_evader:
            # run away, but prefer staying mobile (not squeezing into dead-ends)
            # primary: maximize distance; secondary: maximize mobility; tertiary: prefer diagonals/certain ordering
            score = dist * 1000 + mob
            cand = (score, -mob, dx, dy)
        else:
            # pursuer: reduce distance; if tied, increase mobility and avoid stepping into tight regions
            score = -dist * 1000 + mob
            cand = (score, -mob, dx, dy)

        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]