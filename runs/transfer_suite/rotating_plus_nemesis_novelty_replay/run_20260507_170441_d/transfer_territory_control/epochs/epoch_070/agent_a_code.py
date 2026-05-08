def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    unclaimed = []
    for c in (observation.get("unclaimed_cells") or []):
        try:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                unclaimed.append((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0] if inb(sx, sy) else [1, 0] if inb(sx + 1, sy) else [-1, 0] if inb(sx - 1, sy) else [0, 1] if inb(sx, sy + 1) else [0, -1]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    best = -10**18
    for x, y in unclaimed[:200]:
        d = man(sx, sy, x, y)
        adj_opp = 1 if max(abs(ox - x), abs(oy - y)) == 1 else 0
        center_bias = -(abs(x - (w // 2)) + abs(y - (h // 2))) * 0.01
        sc = -d + 6 * adj_opp + center_bias
        if sc > best:
            best = sc
            target = (x, y)

    if target is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    best_move = moves[0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = man(nx, ny, tx, ty)
        adj_opp = 1 if max(abs(ox - nx), abs(oy - ny)) == 1 else 0
        val = -d + 3 * adj_opp
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]