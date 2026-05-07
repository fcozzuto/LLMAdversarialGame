def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    best = None  # (lead, -selfdist, selfdist, tx, ty)
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if (tx, ty) in obstacles:
            continue
        dxs = tx - sx
        dys = ty - sy
        selfdist = (dxs if dxs >= 0 else -dxs)
        dys_abs = dys if dys >= 0 else -dys
        selfdist = selfdist if selfdist > dys_abs else dys_abs  # chebyshev

        dxo = tx - ox
        dyo = ty - oy
        oppdist = (dxo if dxo >= 0 else -dxo)
        dyo_abs = dyo if dyo >= 0 else -dyo
        oppdist = oppdist if oppdist > dyo_abs else dyo_abs

        lead = oppdist - selfdist  # positive means we are closer
        key = (lead, -selfdist, selfdist, tx, ty)
        if best is None or key > best:
            best = key

    if best is None:
        return [0, 0]

    tx, ty = int(best[3]), int(best[4])
    ddx = tx - sx
    ddy = ty - sy
    dx = 0 if ddx == 0 else (1 if ddx > 0 else -1)
    dy = 0 if ddy == 0 else (1 if ddy > 0 else -1)
    return [dx, dy]