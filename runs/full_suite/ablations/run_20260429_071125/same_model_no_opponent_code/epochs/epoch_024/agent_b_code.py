def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        if (sx, sy) in resources:
            return [0, 0]
        rx, ry = None, None
        bestd = 10**9
        for x, y in resources:
            d = abs(x - sx)
            e = abs(y - sy)
            cd = d if d > e else e
            if cd < bestd or (cd == bestd and (x < rx or (x == rx and y < ry))):
                bestd = cd
                rx, ry = x, y
        tx, ty = rx, ry
    else:
        tx, ty = ox, oy

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if resources:
            d1 = abs(tx - nx)
            e1 = abs(ty - ny)
            cd1 = d1 if d1 > e1 else e1
            d2 = abs(tx - ox)
            e2 = abs(ty - oy)
            cd2 = d2 if d2 > e2 else e2
            key = (-cd2 + cd1, cd1, dx, dy)
        else:
            d1 = abs(tx - nx)
            e1 = abs(ty - ny)
            cd1 = d1 if d1 > e1 else e1
            key = (cd1, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move