def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer resources closer to us than opponent; otherwise pick the best compromise.
        score = (od - sd, -sd, -((rx * 31 + ry) % 997))
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dcur = dist((nx, ny), (tx, ty))
        # Secondary: avoid moving into squares that are also closer to opponent than to us.
        nd = dist((ox, oy), (tx, ty))
        # compute relative advantage at the target after move
        adv = (nd - dcur, -dcur, -((nx * 17 + ny) % 991))
        val = (adv, -abs(dx) - abs(dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]