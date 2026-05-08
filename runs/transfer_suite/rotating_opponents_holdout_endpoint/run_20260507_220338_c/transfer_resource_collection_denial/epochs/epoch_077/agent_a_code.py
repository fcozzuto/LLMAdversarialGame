def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        return [0, 0]

    best_target = resources[0]
    best_d = (best_target[0] - sx) * (best_target[0] - sx) + (best_target[1] - sy) * (best_target[1] - sy)
    for x, y in resources[1:]:
        d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        if d < best_d:
            best_d, best_target = d, (x, y)

    tx, ty = best_target
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        d_self = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        d_opp = (tx - ox) * (tx - ox) + (ty - oy) * (ty - oy)
        score = -d_self + 0.2 * (d_opp - d_self)
        if score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]