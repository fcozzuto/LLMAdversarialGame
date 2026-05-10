def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    edge_unclaimed = []
    for x, y in unclaimed:
        if x == 0 or x == w - 1 or y == 0 or y == h - 1:
            edge_unclaimed.append((x, y))
    if edge_unclaimed:
        tx, ty = min(edge_unclaimed, key=lambda c: man(ox, oy, c[0], c[1]))
    elif unclaimed:
        tx, ty = min(unclaimed, key=lambda c: man(ox, oy, c[0], c[1]))
    else:
        tx, ty = (w // 2, h // 2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0
        cell = (nx, ny)

        v = 0.0
        dcur = man(sx, sy, tx, ty)
        dnext = man(nx, ny, tx, ty)
        v += (dcur - dnext) * 2.2

        if cell in unclaimed: v += 4.2
        elif cell in self_terr: v += 0.7
        elif cell in opp_terr: v += 2.8  # flipping on entry

        # discourage being "too close" to opponent unless we capture
        adj = max(abs(nx - ox), abs(ny - oy))
        if adj <= 1:
            if cell in unclaimed or cell in opp_terr:
                v += 1.0
            else:
                v -= 2.4

        # mild anti-stagnation
        if dx == 0 and dy == 0:
            v -= 0.6

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]