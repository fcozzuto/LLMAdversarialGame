def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = md(nx, ny, ox, oy)
            if best is None or key > best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best_key = None
    best_move = valid[0]
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_for_move = None
        for rx, ry in resources:
            d1 = md(nx, ny, rx, ry)
            d2 = md(ox, oy, rx, ry)
            steal = d2 - d1  # positive if we get there sooner than opponent
            # Also prefer being closer to a valuable spot even if steal is small
            key = steal * 10 - d1
            if best_for_move is None or key > best_for_move:
                best_for_move = key
        # Break ties by maximizing distance from opponent (deterministic)
        key2 = (best_for_move, md(nx, ny, ox, oy))
        if best_key is None or key2 > best_key:
            best_key = key2
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]