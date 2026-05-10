def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_t.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    if unclaimed:
        uc_list = list(unclaimed)[:80]
    else:
        uc_list = []

    if opp_t:
        ot_list = list(opp_t)[:80]
    else:
        ot_list = []

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        val = 0.0

        if cell in unclaimed:
            val += 3.5
        if cell in opp_t:
            val += 3.0  # flipping on entry is enabled

        if uc_list:
            md_uc = 10**9
            for tx, ty in uc_list:
                d = abs(nx - tx) + abs(ny - ty)
                if d < md_uc:
                    md_uc = d
            val += -0.06 * md_uc
        else:
            val += -0.02 * (abs(nx - ox) + abs(ny - oy))

        if ot_list and (nx, ny) not in opp_t:
            md_ot = 10**9
            for tx, ty in ot_list:
                d = abs(nx - tx) + abs(ny - ty)
                if d < md_ot:
                    md_ot = d
            val += -0.03 * md_ot

        if cell in self_t:
            val += 0.1  # slight bias to remain stable

        if val > best[1]:
            best = ((dx, dy), val)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]