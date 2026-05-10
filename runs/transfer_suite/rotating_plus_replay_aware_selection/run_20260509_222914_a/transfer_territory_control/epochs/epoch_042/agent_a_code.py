def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w)
        h = int(h)
    except:
        w = 8
        h = 8

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or sp
    try:
        sx, sy = int(sp[0]), int(sp[1])
        ox, oy = int(op[0]), int(op[1])
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inside(x, y):
                unclaimed.append((x, y))

    opp_ter = []
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inside(x, y):
                opp_ter.append((x, y))

    best_target = None
    if unclaimed:
        # Pick nearest unclaimed; tie-break deterministically by coordinates
        best_target = min(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    elif opp_ter:
        ax = sum(x for x, _ in opp_ter) / len(opp_ter)
        ay = sum(y for _, y in opp_ter) / len(opp_ter)
        # Choose cell closest to centroid among territory
        best_target = min(opp_ter, key=lambda t: ((t[0] - ax) ** 2 + (t[1] - ay) ** 2, t[0], t[1]))
    else:
        best_target = (ox, oy)

    tx, ty = best_target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if inside(nx, ny):
                dist = abs(nx - tx) + abs(ny - ty)
                moves.append((dist, abs(dx) + abs(dy), nx, ny, dx, dy))
    if not moves:
        # If no step possible, return [0,0] if blocked-free else still return something
        return [0, 0]

    moves.sort()
    return [int(moves[0][4]), int(moves[0][5])]