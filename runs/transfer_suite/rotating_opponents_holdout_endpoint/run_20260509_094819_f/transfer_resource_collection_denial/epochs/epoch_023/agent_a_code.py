def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target selection: maximize reach advantage, but avoid contesting near opponent's row band.
    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        row_pen = 0
        if abs(ry - oy) <= 1:
            row_pen = 3  # deter getting into opponent's likely sweep lane
        key = (adv - row_pen, -sd, -abs(rx - sx), -abs(ry - sy), -rx - ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best[1], best[2]

    # Greedy one-step movement toward target with tie-break: avoid getting too close to opponent.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_to = man(nx, ny, tx, ty)
            self_close = man(nx, ny, ox, oy)
            # Prefer staying away from opponent when all else is equal.
            # Also avoid stepping onto obstacle adjacency if it blocks.
            score = (-(d_to), self_close, -abs(nx - tx) - abs(ny - ty), -abs(nx - sx) - abs(ny - sy))
            moves.append((score, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True, key=lambda x: x[0])
    return [int(moves[0][1]), int(moves[0][2])]