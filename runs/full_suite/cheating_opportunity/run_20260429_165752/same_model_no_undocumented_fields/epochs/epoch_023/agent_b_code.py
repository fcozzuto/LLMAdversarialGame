def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        tx, ty = resources[0]
        bestd = -1
        for x, y in resources:
            d = abs(x - sx)
            e = abs(y - sy)
            cd = d if d > e else e
            if bestd < 0 or cd < bestd:
                bestd = cd
                tx, ty = x, y
        bestm = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny):
                d = abs(tx - nx)
                e = abs(ty - ny)
                cd = d if d > e else e
                if cd < bestm[0] or (cd == bestm[0] and (dx, dy) < (bestm[1], bestm[2])):
                    bestm = (cd, dx, dy)
        return [bestm[1], bestm[2]]

    # No resources: move to increase distance from opponent if possible
    bestm = (-1, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny):
            d = abs(nx - ox)
            e = abs(ny - oy)
            cd = d if d > e else e
            if cd > bestm[0] or (cd == bestm[0] and (dx, dy) < (bestm[1], bestm[2])):
                bestm = (cd, dx, dy)
    if bestm[0] >= 0:
        return [bestm[1], bestm[2]]
    return [0, 0]