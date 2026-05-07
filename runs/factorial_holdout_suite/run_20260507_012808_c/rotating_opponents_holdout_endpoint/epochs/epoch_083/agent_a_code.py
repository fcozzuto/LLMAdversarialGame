def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_key_from(posx, posy):
        best = None
        for rx, ry in resources:
            ds = man(posx, posy, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds
            edge_pen = (rx in (0, w - 1)) + (ry in (0, h - 1))
            key = (adv, -ds, -edge_pen, -rx, -ry)
            if best is None or key > best:
                best = key
        return best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        key = best_key_from(nx, ny)
        # slight preference for reducing distance to current best race target
        val = (key[0], key[1], key[2], -abs(dx) - abs(dy), key[3], key[4])
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]