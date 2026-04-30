def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        best_for_move = None
        for rx, ry in resources:
            dsx = nx - rx
            if dsx < 0: dsx = -dsx
            dsy = ny - ry
            if dsy < 0: dsy = -dsy
            ds = dsx if dsx > dsy else dsy

            dox = ox - rx
            if dox < 0: dox = -dox
            doy = oy - ry
            if doy < 0: doy = -doy
            do = dox if dox > doy else doy

            score = (do - ds, -ds, -do)
            if best_for_move is None or score > best_for_move:
                best_for_move = score

        if best_for_move is None:
            continue
        if best_score is None or best_for_move > best_score:
            best_score = best_for_move
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]