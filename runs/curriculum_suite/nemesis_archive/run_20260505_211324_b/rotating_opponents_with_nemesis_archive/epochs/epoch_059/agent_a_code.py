def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for o in (observation.get("obstacles") or []):
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = None
    for dx, dy, nx, ny in moves:
        best_adv = None
        best_md = None
        for rx, ry in resources:
            if not (isinstance(rx, int) and isinstance(ry, int)):
                continue
            if (rx, ry) in obstacles:
                continue
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - my_d  # positive: we are closer than opponent
            if (best_adv is None) or (adv > best_adv) or (adv == best_adv and my_d < best_md):
                best_adv, best_md = adv, my_d
        if best_adv is None:
            continue
        # If we can't beat them to anything (adv<=0), fall back to nearest resource;
        # otherwise, maximize advantage (interception).
        key = (0 if best_adv <= 0 else 1, best_adv, -best_md, dx, dy)
        if best_move is None or key > best_move[0]:
            best_move = (key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]