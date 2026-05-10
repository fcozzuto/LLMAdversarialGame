def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    actions = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("chase" in role) or ("hunter" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in actions:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best = None
    best_score = None

    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        d = dist2(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)

        if pursuer:
            if nx == ox and ny == oy:
                score = 10**9
            else:
                # Reduce distance; prefer routes with more mobility to avoid getting zigzag-pinned.
                score = (-d * 5) + (fn * 1.5) - (dist2(sx, sy, ox, oy) * 0.1)
        else:
            # Evader: maximize distance; avoid dead-ends; also don't step into positions with very low mobility.
            score = (d * 5) + (fn * 1.2) - (4.0 - min(fn, 4)) * 2.0

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: prefer not staying, then smallest |dx|+|dy|.
            stay_best = (best[0] == 0 and best[1] == 0)
            stay_new = (dx == 0 and dy == 0)
            if stay_best and not stay_new:
                best = (dx, dy)
            elif (abs(dx) + abs(dy)) < (abs(best[0]) + abs(best[1])):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]