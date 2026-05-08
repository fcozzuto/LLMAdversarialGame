def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target_x = ox
    target_y = oy

    def neighbor_free_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs:
                    c += 1
        return c

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        cheb = max(abs(nx - ox), abs(ny - oy))
        man = abs(nx - ox) + abs(ny - oy)

        # Axis-cut heuristic: prefer aligning with opponent on x or y when it doesn't worsen distance.
        align_bonus = 0
        if nx == target_x:
            align_bonus += 2
        if ny == target_y:
            align_bonus += 2
        # If we can't align, prefer reducing the larger coordinate gap.
        gapx, gapy = abs(nx - ox), abs(ny - oy)
        align_bonus += 0.01 * (min(gapx, gapy) - max(abs(sx - ox), abs(sy - oy)))

        # Mobility/escape penalty: avoid positions that leave us "surrounded"/near obstacles too much.
        # Also mildly prefer lower opponent-neighbor mobility from their side.
        opp_mob_pen = 0
        # approximate opponent escape at their current spot (static, deterministic)
        opp_mob = neighbor_free_count(ox, oy)
        opp_mob_pen -= 0.02 * opp_mob

        # Wall/obstacle pressure: slightly prefer moving toward edges if it reduces cheb.
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        edge_bonus = 0.03 * (4 - edge)

        # Objective: primarily minimize cheb; tie-break by man, then by align, then by deterministic lexical order.
        v = (-1000 * cheb) + (-10 * man) + align_bonus + opp_mob_pen + edge_bonus - 0.001 * (dx * dx + dy * dy)

        cand = (v, -cheb, -man, align_bonus, edge_bonus, dx, dy)
        if best is None or cand > best:
            best = cand
            bestv = v

    if best is None:
        return [0, 0]
    return [int(best[-2]), int(best[-1])]