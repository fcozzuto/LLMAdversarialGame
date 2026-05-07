def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = p[0], p[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = r[0], r[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    bs = None
    for tx, ty in resources:
        sd = md((sx, sy), (tx, ty))
        od = md((ox, oy), (tx, ty))
        # Aim for resources we can reach first (od advantage decreases score)
        score = (sd - 1.15 * od, sd, abs(tx - ox) + abs(ty - oy))
        if best is None or score < bs:
            best, bs = (tx, ty), score

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [
        (dx, dy), (dx, 0), (0, dy), (-dx, dy), (dx, -dy),
        (-dx, 0), (0, -dy), (-dx, -dy), (0, 0)
    ]
    for ndx, ndy in moves:
        nx, ny = sx + ndx, sy + ndy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(ndx), int(ndy)]
    return [0, 0]