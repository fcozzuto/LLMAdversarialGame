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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    best_key = (-10**18, 10**9, 10**9, 10**9)
    cx, cy = w // 2, h // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in ob:
            continue

        # Contention objective: maximize our advantage over opponent for the most relevant resource,
        # where "resource_denier" style play rewards contesting resources the opponent targets.
        worst_adv = 10**18
        best_resource_dist = 10**18
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in ob:
                continue
            my = md(nx, ny, rx, ry)
            opp = md(ox, oy, rx, ry)
            # Opponent advantage when opp closer; we want to reduce that gap (maximize opp - my).
            adv = opp - my
            if adv < worst_adv:
                worst_adv = adv
            if my < best_resource_dist:
                best_resource_dist = my

        # Extra structure: prefer moving toward center unless that reduces contention advantage.
        center_bias = md(nx, ny, cx, cy)
        # Key: primarily maximize worst_adv, then minimize our distance to the closest resource,
        # then minimize center distance, then deterministic tie-break by (dx,dy).
        key = (worst_adv, -best_resource_dist, -center_bias, dx * 10 + dy)
        if key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]