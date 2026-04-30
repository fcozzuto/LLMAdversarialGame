def choose_move(observation):
    W = observation.get("grid_width") or 8
    H = observation.get("grid_height") or 8
    W = int(W); H = int(H)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_val = None

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H: 
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            dres = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            dop = cheb(nx, ny, ox, oy)
            val = (-dres * 10) + dop
        else:
            val = cheb(nx, ny, ox, oy)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move