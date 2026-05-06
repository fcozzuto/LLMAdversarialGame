def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        sx = min(max(sx, 0), w - 1)
        sy = min(max(sy, 0), h - 1)
        if not valid(sx, sy):
            for yy in range(h):
                for xx in range(w):
                    if valid(xx, yy):
                        sx, sy = xx, yy
                        break
                else:
                    continue
                break

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
    resources = resources if resources else None

    def best_target():
        if resources:
            best = None
            bestd = None
            for rx, ry in resources:
                d = abs(rx - sx) + abs(ry - sy)
                if best is None or d < bestd or (d == bestd and (rx, ry) < best):
                    best = (rx, ry)
                    bestd = d
            return best
        return (ox, oy)

    tx, ty = best_target()

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = abs(tx - nx) + abs(ty - ny)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]