def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1)]
    myc = (sx, sy)

    stc = int(observation.get("self_territory_count", 0) or 0)
    otc = int(observation.get("opponent_territory_count", 0) or 0)

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                unclaimed.append((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    target_list = resources if resources else (unclaimed if unclaimed else [((w - 1 + ox) // 2, (h - 1 + oy) // 2)])
    if stc >= otc:
        tx, ty = ox, oy
    else:
        tx, ty = target_list[0]
        best = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
        for x, y in target_list[1:]:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if d < best:
                best, tx, ty = d, x, y

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_target = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        cell_bonus = 0
        if (nx, ny) in unclaimed:
            cell_bonus += 8
        if (nx, ny) in obs:
            cell_bonus -= 1000
        if resources and (nx, ny) in set(resources):
            cell_bonus += 12
        val = -d_target + (0.2 * d_opp if stc >= otc else 0.05 * d_opp) + cell_bonus
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]