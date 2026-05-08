def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_now = abs(ox - sx) + abs(oy - sy)
        d_next = abs(ox - nx) + abs(oy - ny)
        gain = d_now - d_next
        key = (gain, -d_next, -abs(nx - ox) - abs(ny - oy), -abs(nx - sx) - abs(ny - sy))
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best