def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def nearest_obst_dist(x, y):
        if not ob:
            return 99
        md = 99
        for px, py in ob:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    # Evader: head to farthest corner/edge line; pursuer: minimize distance with obstacle pressure.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    target = None
    if not pursuer:
        target = corners[0]
        best = -1
        for c in corners:
            d = abs(c[0] - ox) + abs(c[1] - oy)
            if d > best:
                best = d
                target = c

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in ob:
            continue

        d = manh(nx, ny)
        obst = nearest_obst_dist(nx, ny)  # prefer staying away from obstacles
        ed = edge_dist(nx, ny)  # prefer some clearance

        # Deterministic scoring (no randomness). Larger is better for both roles.
        if pursuer:
            # Want small d, large obstacle clearance, and some edge avoidance to reduce being blocked.
            score = (-d * 100) + (obst * 3) + (ed * 1)
        else:
            tx, ty = target
            # Want to increase d and move toward chosen far corner while avoiding obstacles.
            corner_d = abs(nx - tx) + abs(ny - ty)
            score = (d * 100) - (corner_d * 2) + (obst * 2) + (ed * 0.5)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]