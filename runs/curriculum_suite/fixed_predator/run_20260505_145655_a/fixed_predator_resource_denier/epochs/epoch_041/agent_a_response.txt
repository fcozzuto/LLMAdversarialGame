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
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def obstacle_penalty(nx, ny):
        if (nx, ny) in obstacles:
            return 10**9
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in obstacles:
                    pen += 2
        return pen

    best = [0, 0]
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Compute best competitive advantage for resources from this candidate cell.
        local_best = -10**18
        nearest = 10**9
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            nearest = selfd if selfd < nearest else nearest
            # Strongly prefer resources where we are closer than opponent; still allow contested grabs.
            sc = (oppd - selfd) * 6 - selfd
            local_best = sc if sc > local_best else local_best

        # Densify by rewarding moving generally toward resources to reduce "non-improving" dithering.
        sc2 = local_best - 0.8 * nearest - 0.7 * obstacle_penalty(nx, ny)

        if sc2 > best_sc:
            best_sc = sc2
            best = [dx, dy]

    return best