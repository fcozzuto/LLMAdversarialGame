def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center_x, center_y = (w - 1) // 2, (h - 1) // 2

    if not resources:
        # drift to center while avoiding obstacles
        bestm = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny, dx, dy = sx, sy, 0, 0
            key = (abs(nx - center_x) + abs(ny - center_y), dx, dy)
            if key < bestm:
                bestm = key
        return [bestm[1], bestm[2]]

    # Pre-filter resources into valid positions
    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                res.append((rx, ry))
    if not res:
        return [0, 0]

    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ndx, ndy = dx, dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            ndx, ndy = 0, 0

        # Immediate return if can grab resource this turn
        on_resource = 1 if (nx, ny) in set(res) else 0

        best_adv = -10**9
        can_take_soon = 0
        best_me_dist = 10**9
        best_center = abs(nx - center_x) + abs(ny - center_y)

        for rx, ry in res:
            me_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            if me_d < best_me_dist:
                best_me_dist = me_d
            adv = opp_d - me_d  # positive means we are closer than opponent
            if adv > best_adv:
                best_adv = adv
            if me_d <= 1 and opp_d > 1:
                can_take_soon = 1

        # Combine: prefer immediate grab, then deny (advantage), then quick access, then center
        # Deterministic ordering via tuple: smaller is better
        key = (
            -on_resource * 1000000 - can_take_soon * 20000,
            -best_adv,
            best_me_dist,
            best_center,
            ndx, ndy
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = (ndx, ndy)

    return [int(best_move[0]), int(best_move[1])]