def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if (tx, ty) not in obstacles:
                resources.append((tx, ty))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(nx, ny):
        # Primary: maximize advantage over opponent on the best reachable resource.
        # Secondary: prefer smaller self distance; tertiary: slightly prefer movement toward resources.
        best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            adv = oppd - selfd
            sc = adv * 12 - selfd * 1.1
            # Mild preference for resources that are currently contested (opponent close too).
            sc += max(0, 7 - oppd) * 0.25
            if sc > best:
                best = sc
        return best

    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = cell_score(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]