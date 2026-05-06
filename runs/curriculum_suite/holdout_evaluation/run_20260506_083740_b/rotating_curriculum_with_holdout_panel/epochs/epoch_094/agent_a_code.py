def choose_move(observation):
    w = int(observation.get("grid_width", 1) or 1)
    h = int(observation.get("grid_height", 1) or 1)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if resources:
        tx, ty = resources[0]
        best = abs(ox - tx) + abs(oy - ty)
        for rx, ry in resources[1:]:
            d = abs(ox - rx) + abs(oy - ry)
            if d < best or (d == best and (rx + ry) < (tx + ty)):
                best, tx, ty = d, rx, ry
    else:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        score = abs(nx - tx) + abs(ny - ty)
        if (nx, ny) == (tx, ty):
            return [dx, dy]
        if score < best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move