def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obst

    if not resources:
        nx, ny = sx, sy
        for dx, dy in moves:
            tx, ty = sx + dx, sy + dy
            if legal(tx, ty):
                if man(tx, ty, (w - 1) // 2, (h - 1) // 2) < man(nx, ny, (w - 1) // 2, (h - 1) // 2):
                    nx, ny = tx, ty
        return [nx - sx, ny - sy]

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        our_opp_d = man(nx, ny, ox, oy)
        best_adv = None
        best_our_d = None
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - our_d
            if best_adv is None or adv > best_adv or (adv == best_adv and our_d < best_our_d):
                best_adv = adv
                best_our_d = our_d
        # maximize advantage, then get closer quickly, then push away from opponent to deny racing
        key = (best_adv, -best_our_d, -our_opp_d, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]