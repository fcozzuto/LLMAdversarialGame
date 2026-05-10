def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cand = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (10**9, None)

    unclaimed = observation.get("unclaimed_cells") or []
    target_cells = []
    for p in unclaimed:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                target_cells.append((x, y))

    opp_path = observation.get("opponent_path") or []
    for p in opp_path[-6:]:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                target_cells.append((x, y))

    if not target_cells:
        target_cells = [(sx, sy)]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        best_d = 10**9
        worst_opp = -10**9
        for tx, ty in target_cells[:40]:
            d = abs(nx - tx) + abs(ny - ty)
            if d < best_d:
                best_d = d
            od = abs(ox - tx) + abs(oy - ty)
            if od > worst_opp:
                worst_opp = od
        score = best_d * 2 - worst_opp
        if score < best[0]:
            best = (score, (dx, dy))

    if best[1] is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]