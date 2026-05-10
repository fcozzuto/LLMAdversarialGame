def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    p = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    try:
        x, y = int(p[0]), int(p[1])
    except:
        x, y = 0, 0
    try:
        ox, oy = int(op[0]), int(op[1])
    except:
        ox, oy = 0, 0
    obs = observation.get("obstacles", []) or []
    blocks = set()
    for t in obs:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            blocks.add((int(t[0]), int(t[1])))
    opp_terr = observation.get("opponent_territory", []) or []
    opp_set = set()
    for t in opp_terr:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            opp_set.add((int(t[0]), int(t[1])))
    res = observation.get("resources", []) or []
    res_list = []
    for t in res:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            rx, ry = int(t[0]), int(t[1])
            if (rx, ry) not in blocks:
                res_list.append((rx, ry))
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h

    if not inb(x, y):
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in blocks:
            continue
        if (nx, ny) in opp_set:
            val = -10**12
        else:
            d_opp = abs(nx - ox) + abs(ny - oy)
            if res_list:
                d_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res_list)
                val = -2 * d_opp - d_res
                if (nx, ny) in res_list:
                    val += 10**6
            else:
                val = -d_opp
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]