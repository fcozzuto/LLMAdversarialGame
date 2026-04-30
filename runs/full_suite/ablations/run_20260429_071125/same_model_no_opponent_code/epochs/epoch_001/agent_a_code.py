def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = {tuple(p) for p in observation["obstacles"]}
    resources = [tuple(p) for p in observation["resources"]]
    w, h = observation["grid_width"], observation["grid_height"]

    if not resources:
        dx = 0
        dy = 0
        tx = 0 if x > w / 2 else -1
        ty = 0 if y > h / 2 else -1
        if x < w - 1: dx = 1
        if x > 0: dx = -1 if x > w / 2 else dx
        if y < h - 1: dy = 1
        if y > 0: dy = -1 if y > h / 2 else dy
        for ddx, ddy in [(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            nx, ny = x + ddx, y + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    best = None
    best_score = None
    for rx, ry in resources:
        ds = (rx - x) * (rx - x) + (ry - y) * (ry - y)
        do = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
        priority = 0
        if do <= ds:
            priority += 5
            if do <= 2:
                priority += 10
        score = ds + priority * 3
        if best_score is None or score < best_score or (score == best_score and (rx, ry) < best):
            best_score = score
            best = (rx, ry)

    tx, ty = best
    deltas = [(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    curd = (tx - x) * (tx - x) + (ty - y) * (ty - y)
    bestd = None
    bestmove = (0, 0)
    for ddx, ddy in deltas:
        nx, ny = x + ddx, y + ddy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        nd = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        if bestd is None or nd < bestd or (nd == bestd and (ddx, ddy) < bestmove):
            bestd = nd
            bestmove = (ddx, ddy)

    if bestd is not None and bestd <= curd + 1:
        return [bestmove[0], bestmove[1]]

    for ddx, ddy in deltas:
        nx, ny = x + ddx, y + ddy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [ddx, ddy]
    return [0, 0]