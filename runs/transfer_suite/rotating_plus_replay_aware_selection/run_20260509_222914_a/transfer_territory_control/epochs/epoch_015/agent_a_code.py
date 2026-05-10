def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    try:
        sx, sy = int(sp[0]), int(sp[1])
        ox, oy = int(op[0]), int(op[1])
    except Exception:
        sx, sy, ox, oy = 0, 0, 0, 0

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
                if inside(x, y):
                    obstacles.add((x, y))
            except Exception:
                pass

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
                if inside(x, y) and (x, y) not in obstacles:
                    resources.append((x, y))
            except Exception:
                pass

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources:
            dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            dres = 10**9
        damp = abs(ox - nx) + abs(oy - ny)
        score = (-dres, damp, dx, dy)
        if best is None or score > best:
            best = score
            best_move = [dx, dy]
    return best_move if best is not None else [0, 0]