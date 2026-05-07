def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [((ox + sx) // 2, (oy + sy) // 2)]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            score = (-10**9, 10**9, 10**9)
        else:
            best_gain = -10**9
            best_selfd = 10**9
            best_lex = (10**9, 10**9)
            for rx, ry in resources:
                selfd = abs(nx - rx) + abs(ny - ry)
                oppd = abs(ox - rx) + abs(oy - ry)
                gain = oppd - selfd
                if gain > best_gain or (gain == best_gain and (selfd < best_selfd or (selfd == best_selfd and (rx, ry) < best_lex))):
                    best_gain = gain
                    best_selfd = selfd
                    best_lex = (rx, ry)
            score = (best_gain, -best_selfd, -nx - ny)
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]