def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            val = cheb(nx, ny, ox, oy)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Evaluate each move by closeness to nearest resource, and keeping distance from opponent.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        # If we can reach a resource while opponent is farther, prioritize strongly.
        reach_adv = d_opp - d_self
        val = (reach_adv * 1000) - d_self * 3 + cheb(nx, ny, ox, oy) * 0.1
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]] if best else [0, 0]