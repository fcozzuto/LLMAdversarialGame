def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w); h = int(h)
    except:
        w = 8; h = 8
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", sp) or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    olist = observation.get("obstacles") or []
    for p in olist:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    bestd = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        if d < bestd:
            bestd = d
            best = [dx, dy]
    if best is not None:
        return best

    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            return [dx, dy]
    return [0, 0]