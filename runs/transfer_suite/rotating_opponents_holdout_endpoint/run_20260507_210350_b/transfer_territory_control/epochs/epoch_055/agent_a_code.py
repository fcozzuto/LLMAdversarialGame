def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)
    unclaimed = observation.get("unclaimed_cells") or []
    best = None
    best_score = None
    for x, y in dirs:
        nx, ny = sx + x, sy + y
        if not inb(nx, ny):
            continue
        target_x, target_y = ox, oy
        target_found = False
        if unclaimed:
            best_cell = None
            best_cd = None
            for c in unclaimed:
                if not c or len(c) < 2:
                    continue
                tx, ty = int(c[0]), int(c[1])
                if not inb(tx, ty):
                    continue
                d_us = dist(nx, ny, tx, ty)
                d_op = dist(ox, oy, tx, ty)
                margin = d_op - d_us
                if margin > 0:
                    cd = d_us + dist(ox, oy, tx, ty) * 0
                    if best_cell is None or (margin > best_cd) or (margin == best_cd and d_us < best_cell[0]):
                        best_cell = (d_us, tx, ty)
                        best_cd = margin
            if best_cell is not None:
                target_x, target_y = best_cell[1], best_cell[2]
                target_found = True
        sc = -dist(nx, ny, target_x, target_y)
        if target_found:
            sc += 5
            sc += (dist(ox, oy, target_x, target_y) - dist(nx, ny, target_x, target_y))
        else:
            sc += 1
            sc += -(dist(nx, ny, ox, oy))
        if best_score is None or sc > best_score or (sc == best_score and (x, y) < best):
            best_score = sc
            best = (x, y)
    if best is None:
        for x, y in dirs:
            nx, ny = sx + x, sy + y
            if inb(nx, ny):
                return [x, y]
        return [0, 0]
    return [best[0], best[1]]