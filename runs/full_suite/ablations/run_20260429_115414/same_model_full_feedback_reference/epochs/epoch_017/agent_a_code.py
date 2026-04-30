def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if res:
            best_adv = None
            best_self_d = None
            for rx, ry in res:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                adv = od - sd
                if best_adv is None or adv > best_adv or (adv == best_adv and (best_self_d is None or sd < best_self_d)):
                    best_adv, best_self_d = adv, sd
            key = (best_adv, -best_self_d)
        else:
            od = dist(nx, ny, ox, oy)
            key = (od, -dist(nx, ny, sx, sy))
        if best_key is None or key > best_key:
            best_key, best_move = key, (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]