def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                unclaimed.append((x, y))

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if inb(sx, sy) and (sx, sy) in obstacles:
        return [0, 0]

    # Choose deterministic best target: closest unclaimed; tie by (x+y) descending, then x, then y.
    target = None
    if unclaimed:
        best = None
        for x, y in unclaimed:
            if (x, y) in obstacles:
                continue
            d = abs(x - sx) + abs(y - sy)
            key = (d, -(x + y), x, y)
            if best is None or key < best:
                best = key
                target = (x, y)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is not None:
            dist = abs(nx - target[0]) + abs(ny - target[1])
            # Prefer moving closer; also slightly avoid proximity to opponent.
            opp_dist = abs(nx - ox) + abs(ny - oy)
            score = (dist, -opp_dist, dx, dy)
        else:
            # No unclaimed: chase opponent if closer, otherwise move away deterministically.
            cur_d = abs(sx - ox) + abs(sy - oy)
            new_d = abs(nx - ox) + abs(ny - oy)
            score = ((new_d - cur_d), new_d, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]