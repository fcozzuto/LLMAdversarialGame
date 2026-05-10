def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        tx, ty = ox, oy
    else:
        best_key = (-10**18, -10**18, -10**18)
        tx, ty = resources[0]
        for x, y in resources:
            sd = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            race = od - sd  # positive means we are closer
            # Tie-break deterministically by farther from opponent (more likely to deny) and then by coordinates
            key = (race, -od, -sd)
            if key > best_key or (key == best_key and (x + y, x, y) > (tx + ty, tx, ty)):
                best_key = key
                tx, ty = x, y

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy)]
    for ndx, ndy in candidates:
        nx, ny = sx + ndx, sy + ndy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            return [int(ndx), int(ndy)]
    return [0, 0]