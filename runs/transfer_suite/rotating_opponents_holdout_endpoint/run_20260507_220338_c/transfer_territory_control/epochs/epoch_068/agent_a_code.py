def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocks:
                resources.append((x, y))

    if not resources:
        resources = [(w // 2, h // 2)]

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        dopp = abs(nx - ox) + abs(ny - oy)
        score = dres * 2 - dopt(0, 0)  # placeholder safety
        score = dres - 0.15 * dott(dopp)
        if best is None or score < best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]

def dott(x):
    return x

def dopt(a, b):
    return 0