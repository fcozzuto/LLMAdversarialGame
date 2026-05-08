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

    role = str(observation.get("self_role", "pursuer") or "pursuer").lower()
    evade = ("evad" in role) or ("run" in role) or ("away" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

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

    def neighbor_count(x, y):
        c = 0
        for ax, ay in deltas:
            nx, ny = x + ax, y + ay
            if ok(nx, ny):
                c += 1
        return c

    best = None
    best_score = None

    # slight deterministic tie-break preference changes with turn_index to avoid repeating
    t = int(observation.get("turn_index", 0) or 0)
    rot = t % 3
    pref = []
    if rot == 0:
        pref = [(0, 1), (1, 0), (0, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    elif rot == 1:
        pref = [(1, 0), (0, -1), (0, 0), (-1, 0), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    else:
        pref = [(-1, 0), (0, 1), (0, 0), (1, 0), (0, -1), (-1, 1), (1, -1), (-1, -1), (1, 1)]

    for dx, dy in pref:
        x1, y1 = sx + dx, sy + dy
        if not ok(x1, y1):
            continue

        d = cheb(x1, y1)
        mob = neighbor_count(x1, y1)

        # pursuer: minimize distance; evader: maximize distance
        # avoid being trapped: prefer higher mobility (and for pursuer, also avoid low-mobility moves)
        score = (-d if not evade else d) + (mob * (0.12 if not evade else 0.18))

        # encourage obstacle-aware "escape corridors": if evading, add tiny penalty if move would reduce mobility
        # if pursuing, add tiny penalty if it would increase mobility too much while not reducing distance (keeps pressure nearby)
        score += (0.01 * mob if evade else -0.01 * (7 - mob))

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]