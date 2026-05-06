def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    my_first = 10**9
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        if dm - do < my_first:
            my_first = dm - do
    prefer_rush = my_first <= 0

    best_r = None
    best_s = None
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        s = (do - dm) if prefer_rush else (-dm)
        tie = (r[0] + 7 * r[1]) if prefer_rush else (-(r[0] + 7 * r[1]))
        key = (s, tie)
        if best_s is None or key > best_s:
            best_s = key
            best_r = r

    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dmn = dist8((nx, ny), (tx, ty))
        dmy = dist8((sx, sy), (tx, ty))
        don = dist8((ox, oy), (tx, ty))
        # Prefer closing; also prefer making opponent farther when equal.
        val = (-(dmn), -don, (nx == tx and ny == ty), -((dx == 0 and dy == 0)), nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]