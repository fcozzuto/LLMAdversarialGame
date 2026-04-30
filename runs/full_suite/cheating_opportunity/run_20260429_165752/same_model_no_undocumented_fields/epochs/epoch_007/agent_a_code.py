def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for a in obstacles:
        try:
            ax, ay = a[0], a[1]
            obs_set.add((int(ax), int(ay)))
        except Exception:
            pass

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (x, y) in obs_set:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    res_list = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
            res_list.append((rx, ry))
        except Exception:
            pass

    best = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        if res_list:
            best_key_for_move = None
            for rx, ry in res_list:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                key = (od - md, -md, rx, ry)
                if best_key_for_move is None or key > best_key_for_move:
                    best_key_for_move = key
            key2 = (best_key_for_move[0], best_key_for_move[1])
        else:
            key2 = (-cheb(nx, ny, ox, oy), abs(nx - (w // 2)) + abs(ny - (h // 2)))
        if best is None or key2 > best[0]:
            best = (key2, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]