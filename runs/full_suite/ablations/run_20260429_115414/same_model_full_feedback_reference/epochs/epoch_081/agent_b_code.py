def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        tx, ty = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        dist_me = abs(nx - tx) + abs(ny - ty)
        dist_op = abs(nx - ox) + abs(ny - oy)
        score = -dist_me + 0.1 * dist_op
        if (nx, ny) == (tx, ty):
            score += 1000
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if dx * dx + dy * dy < best_move[0] * best_move[0] + best_move[1] * best_move[1]:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]