def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    # Choose target with advantage: maximize (opp_dist - my_dist), then minimize my_dist
    target = None
    if resources:
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od - myd, -myd)  # maximize delta, then maximize -myd (i.e., minimize myd)
            if best_key is None or key > best_key:
                best_key = key
                target = (rx, ry)

    # If no resources, head to center
    if target is None:
        target = (w // 2, h // 2)

    # Pick move that best improves to target, while keeping distance from opponent and avoiding obstacles
    best_move = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            myd = cheb(nx, ny, target[0], target[1])
            od = cheb(ox, oy, target[0], target[1])
            # Prefer smaller my distance, and larger distance from opponent to the target region
            # (also slightly prefer larger direct separation from opponent).
            score = (-myd, (od - myd), cheb(nx, ny, ox, oy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]