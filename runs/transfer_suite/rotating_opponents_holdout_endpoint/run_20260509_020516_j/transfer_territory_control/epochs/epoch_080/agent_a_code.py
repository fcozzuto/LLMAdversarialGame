def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (W - 1, H - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in blocked:
                unclaimed.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if unclaimed:
        targets = sorted(unclaimed, key=lambda t: (manh((sx, sy), t), t[0], t[1]))
        tx, ty = targets[0]
    else:
        tx = 0 if ox > (W - 1) // 2 else W - 1
        ty = 0 if oy > (H - 1) // 2 else H - 1
        if (tx, ty) in blocked:
            tx = max(0, min(W - 1, sx + (1 if tx > sx else -1 if tx < sx else 0)))
            ty = max(0, min(H - 1, sy + (1 if ty > sy else -1 if ty < sy else 0)))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in blocked:
            continue
        d = manh((nx, ny), (tx, ty))
        score = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    if best is not None:
        return best[1]
    return [0, 0]