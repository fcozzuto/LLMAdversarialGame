def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in (observation.get("resources") or [])]
    obstacles = {tuple(p) for p in (observation.get("obstacles") or [])}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_dists = []
    if resources:
        for r in resources:
            opp_dists.append(man((ox, oy), r))
        op_d = min(opp_dists)
    else:
        op_d = 0

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            my_d = min(man((nx, ny), r) for r in resources)
            dist_to_op = max(0, man((nx, ny), (ox, oy)))
            score = (op_d - my_d) * 10 - my_d
            score += dist_to_op * 0.15
            if (nx, ny) in resources:
                score += 1000
        else:
            # If no resources known, head to opponent's own side to pressure
            tx = 0 if ox > sx else w - 1
            ty = 0 if oy > sy else h - 1
            score = -man((nx, ny), (tx, ty)) + 0.05 * man((nx, ny), (ox, oy))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]