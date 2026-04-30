def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    rem = int(observation.get("remaining_resource_count", 0) or 0)
    endgame = rem <= 4

    best = None
    bestv = -10**18
    if resources:
        # deterministic: tie-break by lex dx,dy order
        for dx, dy in sorted(legal):
            nx, ny = sx + dx, sy + dy
            dres = min(man(nx, ny, rx, ry) for rx, ry in resources)
            dop = man(nx, ny, ox, oy)
            v = -dres
            if endgame:
                v += 0.5 * dop
            else:
                v += 0.1 * dop
            if v > bestv:
                bestv = v
                best = (dx, dy)
    else:
        for dx, dy in sorted(legal):
            nx, ny = sx + dx, sy + dy
            v = man(nx, ny, ox, oy)  # maximize distance from opponent
            if v > bestv:
                bestv = v
                best = (dx, dy)

    return [int(best[0]), int(best[1])]