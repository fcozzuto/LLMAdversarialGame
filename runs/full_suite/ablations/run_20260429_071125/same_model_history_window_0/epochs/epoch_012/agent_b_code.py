def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set(map(tuple, observation.get("obstacles") or []))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def md(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    resources_list = [tuple(r) for r in resources if tuple(r) not in obs]
    if not resources_list:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = md((nx, ny), (ox, oy))
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return list(best[1]) if best is not None else [0, 0]

    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = min(md((nx, ny), r) for r in resources_list)
        op_d = min(md((ox, oy), r) for r in resources_list)
        score = (op_d - my_d) * 100 - my_d - (abs(dx) + abs(dy))
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]