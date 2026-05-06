def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(0, 0), (0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cur_opp = cheb((sx, sy), (ox, oy))

    if resources:
        best = None
        best_key = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            if not inb(tx, ty) or (tx, ty) in obs:
                continue
            dself = cheb((sx, sy), (tx, ty))
            dopp = cheb((ox, oy), (tx, ty))
            key = (dself - dopp, dself, tx, ty)  # prefer resources we are relatively closer to
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)

        if best is not None:
            tx, ty = best
            best_move = (0, 0)
            best_score = None
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not legal(nx, ny):
                    continue
                nd = cheb((nx, ny), (tx, ty))
                node_opp = cheb((nx, ny), (ox, oy))
                score = -nd * 10 + (node_opp - cur_opp)  # keep distance from denier while closing to target
                if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
                    best_score = score
                    best_move = (dx, dy)
            return [int(best_move[0]), int(best_move[1])]

    return [0, 0]