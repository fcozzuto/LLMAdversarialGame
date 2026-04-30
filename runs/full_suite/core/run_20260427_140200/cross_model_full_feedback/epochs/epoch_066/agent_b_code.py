def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if legal(rx, ry):
                resources.append((rx, ry))

    target = None
    if resources:
        target = min(resources, key=lambda p: cheb((mx, my), p))

    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        score = 0
        if target is not None:
            score -= cheb((nx, ny), target)
        if (nx, ny) == (ox, oy):
            score += 5
        if (nx, ny) in resources:
            score += 3
        # discourage moving into potential trap near opponent
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            score -= 1
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]