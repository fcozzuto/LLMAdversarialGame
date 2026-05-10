def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if dirs:
        pass

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        bonus = 3 if (nx, ny) in unclaimed else 0
        score = bonus * 10 - d_to_opp
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is not None:
        return [int(best[0][0]), int(best[0][1])]

    # Fallback: move toward opponent if legal, else stay
    best2 = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            if best2 is None or (abs(nx - ox) + abs(ny - oy)) < (abs(best2[0] - ox) + abs(best2[1] - oy)):
                best2 = (nx, ny)
    if best2 is not None:
        return [int(best2[0] - sx), int(best2[1] - sy)]
    return [0, 0]