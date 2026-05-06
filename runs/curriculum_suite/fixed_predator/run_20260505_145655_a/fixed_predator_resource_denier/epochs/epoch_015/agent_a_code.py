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
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        local_best = -10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            # Out-approach heavily; shorter self path breaks ties.
            sc = (oppd - selfd) * 10 - selfd

            # Small intercept bias: prefer moving in a direction that reduces
            # the "difference" between our and opponent's relative vectors.
            vx, vy = rx - nx, ry - ny
            ux, uy = rx - ox, ry - oy
            dv = (vx * ux + vy * uy)  # larger when directions align
            sc += 0.01 * dv

            if sc > local_best:
                local_best = sc

        if local_best > best[1]:
            best = ([dx, dy], local_best)

    if best[0] is None:
        return [0, 0]
    return best[0]