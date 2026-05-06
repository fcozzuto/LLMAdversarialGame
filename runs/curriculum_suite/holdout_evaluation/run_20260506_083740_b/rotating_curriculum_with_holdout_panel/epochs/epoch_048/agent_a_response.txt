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
    if not resources:
        return [0, 0]

    # Deterministic contested-resource selection: prefer same-row/col as opponent (sweep_rows proxy),
    # then prefer resources we can take before/at opponent.
    res_list = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                row_col = 0
                if rx == ox:
                    row_col = 2
                elif ry == oy:
                    row_col = 2
                elif rx == ox or ry == oy:
                    row_col = 1
                d_me = md(sx, sy, rx, ry)
                d_opp = md(ox, oy, rx, ry)
                lead = d_opp - d_me  # positive if we are closer
                res_list.append((row_col, lead, d_opp, rx, ry, d_me))
    if not res_list:
        return [0, 0]
    res_list.sort(key=lambda t: (-(t[0]), -(t[1]), t[2], t[3], t[4]))
    target = res_list[0][3], res_list[0][4]

    tx, ty = target

    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = md(nx, ny, tx, ty)
        d_opp = md(ox, oy, tx, ty)

        # If we can beat/meet opponent on this target, strongly prefer.
        # Otherwise, move to reduce our disadvantage and avoid letting opponent get a nearer alternate.
        base = d_opp - d_me
        same_line = 0
        if nx == ox:
            same_line = 1
        if ny == oy:
            same_line = 1

        # Consider second-best resource deterministically for robustness (still local).
        alt_best = -10**18
        for rr in res_list[:6]:
            rx, ry = rr[3], rr[4]
            if (rx, ry) == (tx, ty):
                continue
            val = (md(ox, oy, rx, ry) - md(nx, ny, rx, ry)) + (2 if (rx == ox or ry == oy) else 0)
            if val > alt_best:
                alt_best = val
        if alt_best < -10**17:
            alt_best = -10**9

        value = base * 20 + same_line * 3 + alt_best
        if value > best[1]:
            best = ([dx, dy], value)

    return best[0] if best[0] is not None else [0, 0]