def choose_move(observation):
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        try:
            blocked.add((int(p[0]), int(p[1])))
        except:
            pass

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = clamp(int(sx) + dx, int(sy) + dy)
        if (nx, ny) in blocked:
            continue

        dist_o = abs(nx - ox) + abs(ny - oy)
        if resources:
            dist_r = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            dist_center = abs(nx - tx) + abs(ny - ty)
            val = -dist_r * 5 + dist_o * 0.7 - dist_center * 0.05
        else:
            val = dist_o * 2 - (abs(nx - tx) + abs(ny - ty)) * 0.05

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]