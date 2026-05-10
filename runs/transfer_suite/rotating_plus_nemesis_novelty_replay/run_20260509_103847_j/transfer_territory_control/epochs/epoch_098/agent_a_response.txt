def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    opp = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp.add((int(p[0]), int(p[1])))
    mine = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            mine.add((int(p[0]), int(p[1])))
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))
    opp_list = list(opp)
    if not opp_list:
        opp_list = [(ox, oy)]
    un_list = list(unclaimed) if unclaimed else []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)
    ti = int(observation.get("turn_index", 0) or 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # nearest opponent-territory distance from candidate
        dopt = 10**9
        for px, py in opp_list:
            v = abs(nx - px) + abs(ny - py)
            if v < dopt:
                dopt = v
        # immediate flip
        if (nx, ny) in opp:
            val = 1000 - dopt
            # small bonus if this also moves away from opponent position (reduce their chase)
            val += (abs(nx - ox) + abs(ny - oy)) * 0.5
        elif (nx, ny) in unclaimed:
            val = 120 - dopt
            # prefer expanding toward center-ish of opponent cluster
            if opp_list:
                cx = sum(p[0] for p in opp_list) / float(len(opp_list))
                cy = sum(p[1] for p in opp_list) / float(len(opp_list))
                val += (4 - (abs(nx - cx) + abs(ny - cy)) / 2.0)
        elif (nx, ny) in mine:
            val = 8 - dopt * 0.2
        else:
            val = 20 - dopt
        # tie-break deterministically
        tie = (dx * 3 + dy * 7 + ti) & 3
        val -= tie * 0.01
        if val > best[0]:
            best = (val, dx, dy)
    return [int(best[1]), int(best[2])]