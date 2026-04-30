def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set((x, y) for x, y in obstacles)
    cx, cy = w // 2, h // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = (cx, cy)

    if resources:
        best = None  # (metric, selfdist, resx, resy, centerdist)
        for rx, ry in resources:
            selfd = abs(rx - sx) + abs(ry - sy)
            oppd = abs(rx - ox) + abs(ry - oy)
            metric = selfd - oppd  # negative means we're closer
            centerd = abs(rx - cx) + abs(ry - cy)
            cand = (metric, selfd, rx, ry, centerd)
            if best is None or cand < best:
                best = cand
        target = (best[2], best[3])
        best_metric = best[0]
    else:
        target = center
        best_metric = -1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**9, 10**9, 10**9, 0, 0)

    def objective(nx, ny, to_target_dist):
        # If we're not favored for resources, prioritize creating distance from opponent.
        if best_metric > 0:
            oppdist = abs(nx - ox) + abs(ny - oy)
            # minimize (resource distance) while maximizing (opponent distance)
            return (to_target_dist, -oppdist, abs(nx - cx) + abs(ny - cy))
        else:
            # minimize distance to target and slightly prefer center
            return (to_target_dist, abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        to_target_dist = abs(nx - target[0]) + abs(ny - target[1])
        obj = objective(nx, ny, to_target_dist)
        cand = (obj[0], obj[1], obj[2], dx, dy)
        if cand < best_move:
            best_move = cand

    # If all moves blocked (should be rare), stay put.
    if best_move[3] == 0 and best_move[4] == 0 and ((sx, sy) in obs_set):
        return [0, 0]
    return [int(best_move[3]), int(best_move[4])]