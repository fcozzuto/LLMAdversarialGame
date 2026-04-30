def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp_step(dx, dy):
        if dx < -1: dx = -1
        if dx > 1: dx = 1
        if dy < -1: dy = -1
        if dx == 0 and dy == 0:
            return [0, 0]
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target = None
    if resources:
        best = None
        for r in resources:
            if tuple(r) in obstacles:
                continue
            sd = dist((sx, sy), r)
            od = dist((ox, oy), r)
            score = (od - sd, -sd)  # prefer where opponent is farther; then closer to us
            if best is None or score > best[0]:
                best = (score, r)
        target = best[1]
    else:
        target = (w // 2, h // 2)

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    preferred = clamp_step(dx, dy)
    cand = []
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), target)
        oppd = dist((nx, ny), (ox, oy))
        step_good = (abs(mdx - preferred[0]) + abs(mdy - preferred[1]))
        cand.append((step_good, nd, -oppd, [mdx, mdy]))
    cand.sort()
    if cand:
        return cand[0][3]
    return [0, 0]