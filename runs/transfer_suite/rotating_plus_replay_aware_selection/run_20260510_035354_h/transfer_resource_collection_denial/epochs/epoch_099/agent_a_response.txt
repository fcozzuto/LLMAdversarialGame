def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_score(rx, ry):
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Prefer being strictly closer; still take contested if very good.
        # Deterministic tie-break by (do - ds), then smaller ds, then lexicographic.
        return (do - ds, -ds, -rx, -ry)

    resources.sort()
    target = max(resources, key=lambda r: cell_score(r[0], r[1]))

    rx, ry = target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        ns = md(nx, ny, rx, ry)
        no = md(ox, oy, rx, ry)
        # Maximize advantage; then minimize our distance to target; then prefer moving closer in x/y.
        adv = no - ns
        primary = (adv, -ns, -abs(nx - rx) - abs(ny - ry), -(dx == 0 and dy == 0), -dx, -dy)
        if best is None or primary > best[0]:
            best = (primary, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]