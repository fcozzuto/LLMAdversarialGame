def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    uset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    sset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def n_unclaimed(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in uset:
                    c += 1
        return c

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        if (nx, ny) in uset:
            base = 12
        elif (nx, ny) in oset:
            base = 10  # try to flip by entering opponent territory
        elif (nx, ny) in sset:
            base = 2
        else:
            base = 0  # still unclaimed/neutral

        opp_close = dist(nx, ny, ox, oy)
        my_close = dist(nx, ny, ax, ay)  # 0 always here, keep deterministic

        val = base
        val += 2 * n_unclaimed(nx, ny)
        val += 0.15 * my_close
        val += 0.9 * (7 - opp_close)  # move to reduce opponent distance when contesting
        if (nx, ny) in oset:
            val += 3  # emphasize flips
            val -= 0.5 * n_unclaimed(nx, ny) * 0.2  # slight penalty to avoid pointless swap into open area

        # If unclaimed exists, discourage stepping into opponent territory if there is an immediate better unclaimed option
        if uset and (nx, ny) in oset:
            best_unclaimed_d = 10**9
            for tx, ty in uset:
                d = dist(nx, ny, tx, ty)
                if d < best_unclaimed_d:
                    best_unclaimed_d = d
            val -= 0.2 * best_unclaimed_d

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]