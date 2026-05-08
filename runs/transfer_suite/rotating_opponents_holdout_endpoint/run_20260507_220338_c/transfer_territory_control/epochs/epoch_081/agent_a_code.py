def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        resources = [(ox, oy)]

    def bestdist(x, y):
        bd = 10**9
        for tx, ty in resources:
            d = abs(tx - x) + abs(ty - y)
            if d < bd:
                bd = d
        return bd

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocks:
            continue
        d = bestdist(nx, ny)
        key = (d, -abs(nx - ox) - abs(ny - oy), nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]