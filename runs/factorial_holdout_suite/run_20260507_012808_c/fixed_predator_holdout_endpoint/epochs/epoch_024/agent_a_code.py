def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        dopp = abs(nx - ox) + abs(ny - oy)
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d = abs(nx - rx) + abs(ny - ry)
                if d < dmin:
                    dmin = d
            v = -dmin * 100 + doppel_bonus(dopp)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            v = -(abs(nx - cx) + abs(ny - cy)) * 5 + doppel_bonus(dopp)
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best

def doppel_bonus(dopp):
    if dopp <= 1:
        return -10000
    if dopp <= 2:
        return -2000
    return dopp * 3