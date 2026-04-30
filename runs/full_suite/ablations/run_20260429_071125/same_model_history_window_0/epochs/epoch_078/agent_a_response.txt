def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_res = None
    best_val = None
    for rx, ry in resources:
        ds = (sx - rx) * (sx - rx) + (sy - ry) * (sy - ry)
        do = (ox - rx) * (ox - rx) + (oy - ry) * (oy - ry)
        val = ds - 0.3 * do
        if best_val is None or val < best_val or (val == best_val and (rx, ry) < best_res):
            best_val = val
            best_res = (rx, ry)
    if best_res is None:
        best_move = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
                continue
            dpo = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = -dpo
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best_res
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue
        ds = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        do = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = ds - 0.02 * do
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]