def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    try:
        x, y, ox, oy = int(x), int(y), int(ox), int(oy)
    except:
        x, y, ox, oy = 0, 0, 0, 0

    blocks = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocks.add((int(p[0]), int(p[1])))

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h

    if not inb(x, y):
        return [0, 0]

    targets = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            tx, ty = int(p[0]), int(p[1])
            if inb(tx, ty) and (tx, ty) not in blocks:
                targets.append((tx, ty))
    targets.sort()
    if len(targets) > 15:
        targets = targets[:15]

    if targets:
        tx, ty = min(targets, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    else:
        tx, ty = ox, oy  # fall back to safety

    best = None
    bestv = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in blocks:
                continue
            d1 = abs(nx - tx) + abs(ny - ty)
            d2 = abs(nx - ox) + abs(ny - oy)
            v = (-1000 * d1) + (10 * d2)
            key = (v, -abs(dx) - abs(dy), dx, dy)
            if bestv is None or key > best:
                bestv = v
                best = key
                best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move