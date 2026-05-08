def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w // 2 if w else 0), (h // 2 if h else 0)
    tx, ty = cx, cy
    bestk = None

    found = False
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                found = True
                k = (man(ox, oy, x, y) - man(sx, sy, x, y), -man(sx, sy, x, y))
                if bestk is None or k > bestk:
                    bestk = k
                    tx, ty = x, y

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    bestm = (0, 0)
    bestscore = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = man(nx, ny, ox, oy) - man(nx, ny, tx, ty)
        if bestscore is None or score > bestscore:
            bestscore = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]