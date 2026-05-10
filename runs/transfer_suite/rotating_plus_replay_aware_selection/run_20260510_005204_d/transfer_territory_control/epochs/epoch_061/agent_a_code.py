def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target():
        for k in ("unclaimed_cells", "resources"):
            cells = observation.get(k) or []
            best = None
            bestd = 10**9
            for p in cells:
                if not p or len(p) < 2:
                    continue
                x, y = int(p[0]), int(p[1])
                if not inb(x, y):
                    continue
                d = abs(x - sx) + abs(y - sy)
                if d < bestd:
                    bestd = d
                    best = (x, y)
            if best is not None:
                return best
        return (ox, oy)

    tx, ty = best_target()

    best_move = (0, 0)
    best_dist = 10**9
    best_adv = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        adv = (abs(ox - sy) + abs(oy - sx)) - (abs(ox - ny) + abs(oy - nx))
        if d < best_dist or (d == best_dist and adv > best_adv) or (d == best_dist and adv == best_adv and (dx, dy) < best_move):
            best_dist = d
            best_adv = adv
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]