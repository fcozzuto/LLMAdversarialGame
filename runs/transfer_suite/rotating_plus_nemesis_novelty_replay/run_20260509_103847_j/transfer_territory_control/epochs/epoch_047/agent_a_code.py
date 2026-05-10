def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w); h = int(h)
    except:
        w = 8; h = 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy)
    ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    if unclaimed:
        best = None
        bestd = 10**9
        for x, y in unclaimed:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if d < bestd:
                bestd = d
                best = (x, y)
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if dx == 0 and dy == 0:
            dx = 1 if sx < w - 1 else (-1 if sx > 0 else 0)
            dy = 1 if sy < h - 1 else (-1 if sy > 0 else 0)
        return [int(dx), int(dy)]

    dx = sx - ox
    dy = sy - oy
    if dx != 0: dx = 1 if dx > 0 else -1
    if dy != 0: dy = 1 if dy > 0 else -1
    if dx == 0 and dy == 0:
        dx = 1 if sx < w - 1 else (-1 if sx > 0 else 0)
        dy = 0
    return [int(dx), int(dy)]