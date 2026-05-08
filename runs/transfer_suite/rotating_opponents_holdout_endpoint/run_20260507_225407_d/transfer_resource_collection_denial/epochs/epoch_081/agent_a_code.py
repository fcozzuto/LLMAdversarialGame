def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_adv_from(px, py):
        best = None
        for rx, ry in resources:
            ds = md(px, py, rx, ry)
            do = md(ox, oy, rx, ry)
            adv = do - ds
            # Prefer winning targets first; then closer self; then tie-break by resource position
            key = (adv, -ds, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry), ds, do)
        return best

    # Evaluate each move by how much it improves our best advantage; also add proximity pressure.
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        adv_pack = best_adv_from(nx, ny)
        (adv, neg_ds, _neg_rx, _neg_ry), (tx, ty), ds, do = adv_pack
        # If we can reach a resource at least as fast as opponent, strongly prefer it.
        winish = 1 if ds <= do else 0
        key = (winish, adv, -ds, -abs(nx - tx) - abs(ny - ty))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]