def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    obstacle_penalty = 10**6

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h
    def dist(a, b):
        return (a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1])

    if not resources:
        target = (w//2, h//2)
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = x+dx, y+dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            v = dist((nx, ny), target) - 0.05*dist((nx, ny), (ox, oy))
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = x+dx, y+dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = None
        # Pick the resource that gives maximal relative advantage to next position.
        for rx, ry in resources:
            myd = dist((nx, ny), (rx, ry))
            oppd = dist((ox, oy), (rx, ry))
            # Lower is better: myd - oppd. Add tiny deterministic bias to break ties.
            bias = 0.001*(rx - ry)
            rel = myd - oppd + bias
            if my_best is None or rel < my_best:
                my_best = rel

        # Encourage moving closer to some resource and discouraging proximity to opponent a bit.
        opp_prox = dist((nx, ny), (ox, oy))
        score = my_best + 0.02*opp_prox

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move