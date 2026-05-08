def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))

    if not targets:
        oterr = observation.get("opponent_territory") or []
        for p in oterr:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))

    if not targets:
        return [0, 0]

    best = None
    bestd = 10**18
    for x, y in targets:
        d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        if d < bestd or (d == bestd and (x, y) < best):
            bestd = d
            best = (x, y)

    tx, ty = best
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    pref = []
    if abs(tx - sx) >= abs(ty - sy):
        pref = [(-1, 0) if sx > tx else (1, 0), (0, -1) if sy > ty else (0, 1), (0, 0)]
    else:
        pref = [(0, -1) if sy > ty else (0, 1), (-1, 0) if sx > tx else (1, 0), (0, 0)]
    seen = set()
    ordered = []
    for m in pref + moves:
        if m not in seen:
            seen.add(m)
            ordered.append(m)

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]

    return [0, 0]