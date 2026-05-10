def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                targets.append((x, y))
    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if ok(x, y):
                    targets.append((x, y))

    cx, cy = w // 2, h // 2
    if not targets:
        targets = [(cx, cy)]

    def best_target():
        best = None
        bestd = 10**18
        for tx, ty in targets:
            dx, dy = sx - tx, sy - ty
            d = dx * dx + dy * dy
            if d < bestd:
                bestd = d
                best = (tx, ty)
        return best

    tx, ty = best_target()
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    bestm = (0, 0)
    bestscore = 10**18
    # Prefer reducing distance; break ties deterministically by move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if dist < bestscore or (dist == bestscore and (dx, dy) < bestm):
            bestscore = dist
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]