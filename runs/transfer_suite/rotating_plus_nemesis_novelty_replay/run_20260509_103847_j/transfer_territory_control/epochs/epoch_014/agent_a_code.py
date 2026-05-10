def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)

    op_list = list(opT)
    un_list = list(unT)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def min_dist_to_op(x, y):
        if not op_list:
            return 0
        md = 10**9
        for tx, ty in op_list:
            d = manh(x, y, tx, ty)
            if d < md:
                md = d
        return md

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy

        gain = 0
        if (nx, ny) in unT:
            gain = 1
        elif (nx, ny) in opT:
            gain = 2  # capture/flip advantage

        # Prefer expansion that increases distance from opponent unless we can capture now
        d_op = min_dist_to_op(nx, ny)
        # Also bias towards cells closer to unclaimed frontier (but away from obstacles already handled)
        d_un = 0
        if un_list:
            md = 10**9
            for ux, uy in un_list[:20]:
                d = manh(nx, ny, ux, uy)
                if d < md:
                    md = d
            d_un = md

        # Core score: take high-value moves, otherwise keep a defensive buffer (larger d_op) and move toward unclaimed (smaller d_un)
        score = gain * 1000 + d_op * 3 - d_un * 0.6

        # If current position is already in opponent territory, force deterministic retreat unless capturing improves
        if (sx, sy) in opT and gain < 2:
            score -= 200

        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]