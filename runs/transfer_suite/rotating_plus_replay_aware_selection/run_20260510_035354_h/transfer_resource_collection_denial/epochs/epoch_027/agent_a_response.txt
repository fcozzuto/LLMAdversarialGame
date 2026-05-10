def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_score = -10**9

    # Greedy race: prefer moves that reduce our distance to reachable resources
    # while increasing the opponent's closest distance to those same resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # compute min distance to any resource for each agent
        my_min = 10**9
        op_min = 10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            if d_my < my_min:
                my_min = d_my
            d_op = cheb(ox, oy, rx, ry)
            if d_op < op_min:
                op_min = d_op

        # tie-break: also consider how many resources are "ahead" for us
        # (deterministic proxy without pathfinding).
        my_ahead = 0
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) <= cheb(ox, oy, rx, ry):
                my_ahead += 1

        # higher is better
        score = (op_min - my_min) * 100 + my_ahead
        # deterministic micro-preference: favor progress to top-right then downward
        score += (nx * 2 + (h - 1 - ny))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]