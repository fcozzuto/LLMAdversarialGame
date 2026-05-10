def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in blocked

    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                targets.append((x, y))
    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inside(x, y):
                    targets.append((x, y))
    if not targets:
        op = observation.get("opponent_position") or (W - 1, H - 1)
        targets = [(int(op[0]), int(op[1])), (W // 2, H // 2), (0, 0), (W - 1, H - 1)]

    tx, ty = targets[0]
    bestd = None
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        if bestd is None or d < bestd:
            bestd = d
            tx, ty = x, y

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = abs(tx - nx) + abs(ty - ny)
        if bestscore is None or score < bestscore or (score == bestscore and (dx, dy) < best):
            bestscore = score
            best = (dx, dy)

    if best is None:
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            if inside(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]