def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # simple deterministic heuristic: move towards closest resource if safe; else move away from opponent slightly
    best = None
    best_score = -10**9

    # If there are resources, target nearest resource
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # distance to nearest resource from candidate
            d_me = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_opp = cheb(nx, ny, ox, oy)
            score = -(d_me) * 2  # prefer being close to resource
            # discourage moving onto close to opponent
            if d_opp == 0:
                score -= 100
            if score > best_score:
                best_score = score
                best = (dx, dy)
    else:
        # no resources known, try to stay diagonally away or circle center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_to_center = max(abs(nx - cx), abs(ny - cy))
            d_to_opp = max(abs(nx - ox), abs(ny - oy))
            score = -d_to_center*1.0
            if d_to_opp == 0:
                score -= 50
            if score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        best = (0, 0)

    return [int(best[0]), int(best[1])]