def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((int(r[0]), int(r[1])))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    any_resources = len(resources) > 0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = -dist_opp * 2

        if any_resources:
            dmin = None
            for rx, ry in resources:
                if (rx, ry) != (nx, ny):
                    d = abs(nx - rx) + abs(ny - ry)
                    if dmin is None or d < dmin:
                        dmin = d
            if dmin is None:
                dmin = 0
            score += -dmin

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]