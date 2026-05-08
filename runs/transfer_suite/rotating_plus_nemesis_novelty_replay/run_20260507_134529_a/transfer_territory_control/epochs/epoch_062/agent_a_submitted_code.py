def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")

    def cd(a, b):
        ax, ay = a
        bx, by = b
        da = ax - bx
        db = ay - by
        da = -da if da < 0 else da
        db = -db if db < 0 else db
        return da if da > db else db

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center = (w // 2, h // 2)
    opp = (ox, oy)
    best = None
    best_val = -10**18

    targets = []
    if unclaimed:
        targets = sorted(unclaimed)
    elif opp_terr:
        targets = sorted(opp_terr)
    else:
        targets = [center]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        pos = (nx, ny)
        d_target = min(cd(pos, t) for t in targets)
        d_opp = cd(pos, opp)

        val = 0
        if unclaimed:
            val += 1000 if pos in unclaimed else 0
            val += -10 * d_target
        elif opp_terr:
            val += 200 if pos in opp_terr else 0
            val += -6 * d_target
        else:
            val += -2 * cd(pos, center)

        if pos in self_terr:
            val += 3
        if pos in opp_terr:
            val += 30

        if d_opp <= 1:
            val -= 500

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best