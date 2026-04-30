def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    mx, my = int(me[0]), int(me[1])
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
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def cheb(a, b):
        dx = abs(a[0]-b[0])
        dy = abs(a[1]-b[1])
        return dx if dx > dy else dy

    def dist_to_target(target):
        return cheb((mx, my), target)

    def choose_toward(target):
        best = None
        bestd = None
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not legal(nx, ny):
                continue
            d = dist_to_target(target) if False else cheb((nx, ny), target)
            if bestd is None or d < bestd:
                bestd = d
                best = (dx, dy)
        if best is None:
            return (0, 0)
        return best

    if resources:
        # Move to closest resource, then if adjacent to opponent and blocked, try to block
        closest = min(resources, key=lambda r: cheb((mx, my), r))
        dx, dy = choose_toward(closest)
        # If the move would land on the opponent, prefer staying
        nx, ny = mx + dx, my + dy
        if (nx, ny) == (ox, oy):
            return [0, 0]
        return [dx, dy]

    # No visible resources: approach center while avoiding obstacles and staying safe from opponent
    center = (w//2, h//2)
    dx, dy = choose_toward(center)
    nx, ny = mx + dx, my + dy
    if (nx, ny) == (ox, oy):
        # Try a different nearby step to avoid collision
        for sdx, sdy in moves:
            tx, ty = mx + sdx, my + sdy
            if not legal(tx, ty):
                continue
            if (tx, ty) != (ox, oy):
                return [sdx, sdy]
        return [0, 0]
    return [dx, dy]