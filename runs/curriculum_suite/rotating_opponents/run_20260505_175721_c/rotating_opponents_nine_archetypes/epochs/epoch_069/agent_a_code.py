def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    def score_pos(px, py, rx, ry):
        sd = man(px, py, rx, ry)
        od = man(ox, oy, rx, ry)
        # If we can reach no later than opponent, prioritize closer.
        if sd <= od:
            return (0, sd, od)
        # Otherwise, prioritize resources where we reduce the opponent's lead.
        return (1, od - sd, od)

    best_move = None
    best_key = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            chosen = None
            for rx, ry in resources:
                k = score_pos(nx, ny, rx, ry)
                if chosen is None or k < chosen:
                    chosen = k
                    if chosen[0] == 0 and chosen[1] == 0:
                        break
            key = chosen
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]