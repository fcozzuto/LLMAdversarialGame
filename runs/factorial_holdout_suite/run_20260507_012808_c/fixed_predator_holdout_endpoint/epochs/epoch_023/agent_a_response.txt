def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if resources:
        best_res = None
        best_key = None
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            key = (do - ds, -ds, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)
        tx, ty = best_res

        best_move = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            ns = md(nx, ny, tx, ty)
            no = md(nx, ny, ox, oy)
            # Smaller ns is good; larger no is good; tie-break deterministically
            val = (-ns, no, -abs(nx - tx), -abs(ny - ty), dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move toward center while not getting too close to opponent
    cx, cy = w // 2, h // 2
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = (-md(nx, ny, cx, cy), md(nx, ny, ox, oy), nx, ny, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]