def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer unclaimed cells, else resources, else center.
    targets = []
    for x, y in observation.get("unclaimed_cells") or []:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in blocked and (x, y) != (sx, sy):
            targets.append((x, y))

    if not targets:
        for x, y in observation.get("resources") or []:
            x, y = int(x), int(y)
            if inb(x, y) and (x, y) not in blocked and (x, y) != (sx, sy):
                targets.append((x, y))

    if not targets:
        cx, cy = w // 2, h // 2
        targets = [(cx, cy), (cx - 1, cy), (cx, cy - 1), (cx + 1, cy), (cx, cy + 1)]

    # Deterministic tie-break by sorted order.
    targets = sorted(set(t for t in targets if inb(t[0], t[1]) and t not in blocked))

    best = None
    bestd = None
    for tx, ty in targets:
        d = abs(tx - sx) + abs(ty - sy)
        if bestd is None or d < bestd:
            bestd = d
            best = (tx, ty)
        elif d == bestd and (tx, ty) < best:
            best = (tx, ty)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        # Score: closer to target; slight penalty moving away from it; avoid approaching opponent too much.
        md = abs(tx - nx) + abs(ty - ny)
        od = abs(ox - nx) + abs(oy - ny)
        score = (md, -od, dx, dy)
        if bestscore is None or score < bestscore:
            bestscore = score
            bestm = [dx, dy]

    if bestm is None:
        return [0, 0]
    return bestm