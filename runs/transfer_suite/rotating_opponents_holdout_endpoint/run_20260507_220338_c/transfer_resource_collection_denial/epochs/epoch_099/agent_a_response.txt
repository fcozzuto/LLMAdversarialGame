def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    tr = int(observation.get("turns_remaining", 0))
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_key = None
    best_mv = (0, 0)

    # Switch strategy near end: secure nearest if time is short.
    endgame = tr <= 10

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            nx, ny = sx, sy

        # Choose best target for this hypothetical move
        best_resource_key = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            advantage = od - sd  # positive means we're closer
            # If endgame, prioritize self distance strongly; otherwise prioritize blocking opponent.
            if endgame:
                key = (-sd, -advantage, -(rx + ry))
            else:
                # Primary: deny opponent (we want sd small vs od). Secondary: quick collection and symmetry.
                center = abs((rx - (w - 1) * 0.5)) + abs((ry - (h - 1) * 0.5))
                key = (advantage, -sd, -center, -(rx + ry))
            if best_resource_key is None or key > best_resource_key:
                best_resource_key = key

        if best_key is None or best_resource_key > best_key:
            best_key = best_resource_key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]