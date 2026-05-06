def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    me = (sx, sy)
    opp = (ox, oy)

    opp_target = min(resources, key=lambda r: (man(opp, r), r[0], r[1]))

    def self_adv(cell):
        sd = man(me, cell)
        od = man(opp, cell)
        return (od - sd, -sd, cell[0], cell[1])

    best_target = min(resources, key=lambda r: (-self_adv(r)[0], self_adv(r)[1], self_adv(r)[2], self_adv(r)[3]))
    # If we can reach opponent's likely target earlier (or tie-break), steal it.
    sd_opp = man(me, opp_target)
    od_opp = man(opp, opp_target)
    if sd_opp + 1 <= od_opp:
        target = opp_target
    else:
        target = best_target

    tx, ty = target
    # Choose move that minimizes distance to target; deterministic tie-break: prefer dx then dy with fixed ordering.
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        key = (d, -dx, -dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]
    return [best[0], best[1]]