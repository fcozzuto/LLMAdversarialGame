def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obstacle_prox(x, y):
        p = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                p += 1
        return p

    best = None
    best_score = None

    cur_d = man(sx, sy, ox, oy)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    target_corner = max(corners, key=lambda c: man(sx, sy, c[0], c[1]) + man(ox, oy, c[0], c[1]))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        nd = man(nx, ny, ox, oy)
        dist_term = (nd - cur_d) if is_evader else (cur_d - nd)

        # Evader prefers to run toward a far corner; pursuer prefers to stay away from obstacles and tighten space.
        corner_term = (man(nx, ny, target_corner[0], target_corner[1]) if is_evader else -man(nx, ny, target_corner[0], target_corner[1]))
        avoid_term = -obstacle_prox(nx, ny)
        edge_term = edge_dist(nx, ny)

        score = 1000 * dist_term + 5 * corner_term + 2 * avoid_term + (edge_term if not is_evader else -edge_term)

        # Deterministic tie-break: prefer smaller dx,dy lex order when scores equal.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]