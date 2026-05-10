def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best_move = moves[0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        ux = 0
        if (nx, ny) in unclaimed:
            ux = 5000

        do = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Prefer going toward nearby unclaimed if far from opponent
        near_u = 0
        for cx, cy in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)):
            if 0 <= cx < w and 0 <= cy < h and (cx, cy) in unclaimed:
                near_u = 1200

        score = ux + near_u + do - (abs(nx - ox) + abs(ny - oy)) * 2
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    dx, dy = best_move
    if not (dx in (-1, 0, 1) and dy in (-1, 0, 1)):
        return [0, 0]
    return [int(dx), int(dy)]