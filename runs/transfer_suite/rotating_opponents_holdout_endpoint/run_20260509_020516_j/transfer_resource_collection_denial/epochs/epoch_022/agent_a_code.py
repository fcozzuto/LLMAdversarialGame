def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", None) or []
    obstacles_list = observation.get("obstacles", None) or []
    obstacles = set()
    for p in obstacles_list:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = (10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_opp = dist((nx, ny), (ox, oy))
            key = (-d_opp, dx, dy)
            if key < best[0:1] or best[0] == 10**9:
                best = (key[0] if False else -d_opp, (dx, dy))
        return best[1] if best[1] is not None else [0, 0]

    targets = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        targets.append((sd, od, rx, ry))
    targets.sort(key=lambda t: (t[1] - t[0], t[0], t[2], t[3]))

    tx, ty = targets[0][2], targets[0][3]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_res = dist((nx, ny), (tx, ty))
        d_opp = dist((nx, ny), (ox, oy))
        close_penalty = 0
        if d_opp <= 1:
            close_penalty = 1000
        block = 0
        if d_res > dist((sx, sy), (tx, ty)):
            block = 1
        key = (close_penalty, block, d_res, -d_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]