def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if resources:
        tx, ty = min(resources, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - ox) + abs(p[1] - oy), p[0], p[1]))
    else:
        tx, ty = (w // 2, h // 2)

    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_target = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(ox - nx) + abs(oy - ny)
        align = 1 if dx == desired_dx and dy == desired_dy else 0
        score = (-d_target, d_opp, align, -nx, -ny)
        if best is None or score > best[0]:
            best = (score, [dx, dy])
    return best[1] if best is not None else [0, 0]