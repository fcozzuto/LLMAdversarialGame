def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    # If no resources, just stay (deterministic).
    if not resources:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = -10**18
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            if not ok(rx, ry):
                continue
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer than opponent to this resource
            on_resource = 1 if (nx == rx and ny == ry) else 0
            cand = adv * 1000 - sd + on_resource * 100000
            if cand > score:
                score = cand

        # If all resources are blocked/unreachable, fallback to move that minimizes our distance to any resource.
        if score == -10**18:
            fallback = 10**18
            for r in resources:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                rx, ry = r[0], r[1]
                if not ok(rx, ry):
                    continue
                d = dist(nx, ny, rx, ry)
                if d < fallback:
                    fallback = d
            score = -fallback

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move