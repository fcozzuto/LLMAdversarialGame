def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    x, y = int(sp[0]), int(sp[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < W and 0 <= by < H:
                blocked.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < W and 0 <= ry < H and (rx, ry) not in blocked:
                resources.append((rx, ry))

    op = observation.get("opponent_position") or (0, 0)
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H or (nx, ny) in blocked:
            continue

        if resources:
            md = None
            for rx, ry in resources:
                d = abs(rx - nx) + abs(ry - ny)
                if md is None or d < md:
                    md = d
            val = md
        else:
            val = abs(ox - nx) + abs(oy - ny)

        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]