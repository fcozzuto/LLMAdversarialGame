def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obstacle_set = set((p[0], p[1]) for p in obstacles)
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacle_set:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner (smaller sd-od), then closer (smaller sd)
        key = (sd - od, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = cheb(sx, sy, tx, ty)
    oppd = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer reducing distance; slight preference for moving to positions that slow opponent
        n_oppd = cheb(ox, oy, tx, ty)
        # Compute whether this move would likely contest: after move we want nd <= oppd
        contest = 0 if nd <= oppd else 1
        key = (nd, contest, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_key is not None and best_key[0] <= curd:
        return [best_move[0], best_move[1]]

    # If no improvement possible, choose the move that keeps us from moving away most
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue
        nd = cheb(nx, ny, tx, ty)
        key = (nd, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]