def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dmax(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    # Pick target by "advantage" in distance, then by closer self distance, then coordinate
    target = None
    best = None
    for tx, ty in resources:
        sd = dmax(sx, sy, tx, ty)
        od = dmax(ox, oy, tx, ty)
        adv = od - sd
        key = (adv, -sd, -tx, -ty)
        if best is None or key > best:
            best = key
            target = (tx, ty)

    # If no resources, drift toward center to reduce distance to future spawns
    if target is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    # Greedy move toward target; if blocked, choose best alternative by distance reduction
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = dmax(nx, ny, tx, ty)
        # tie-break: prefer moves that also increase opponent distance (to steal advantage)
        no = dmax(nx, ny, ox, oy)
        oppd = dmax(ox, oy, tx, ty)
        key = (-nd, no, -oppd, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]