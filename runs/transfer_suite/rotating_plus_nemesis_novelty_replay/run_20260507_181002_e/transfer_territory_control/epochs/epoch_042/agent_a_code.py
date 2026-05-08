def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    if sx < 0: sx = 0
    if sy < 0: sy = 0
    if sx >= w: sx = w - 1
    if sy >= h: sy = h - 1

    def toset(val):
        s = set()
        if not val:
            return s
        for p in val:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles")) | toset(observation.get("resources"))  # treat resources as blocked if present
    unclaimed = toset(observation.get("unclaimed_cells") or observation.get("unclaimed") or observation.get("empty_cells"))

    if not unclaimed:
        return [0, 0]

    def sign(z):
        return 1 if z > 0 else (-1 if z < 0 else 0)

    best = None
    best_d = 10**9
    for tx, ty in unclaimed:
        if (tx, ty) in obstacles:
            continue
        d = abs(tx - sx) + abs(ty - sy)
        if d < best_d or (d == best_d and (tx, ty) < best):
            best_d = d
            best = (tx, ty)
    if not best:
        return [0, 0]

    tx, ty = best
    dx = sign(tx - sx)
    dy = sign(ty - sy)

    nx, ny = sx + dx, sy + dy
    if (dx, dy) != (0, 0) and 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [int(dx), int(dy)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best2 = (0, 0)
    best2_d = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = abs(tx - nx) + abs(ty - ny)
            if d < best2_d:
                best2_d = d
                best2 = (dx, dy)
    return [int(best2[0]), int(best2[1])]