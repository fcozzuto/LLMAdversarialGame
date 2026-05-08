def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_cells(v):
        out = []
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    out.append((int(p[0]), int(p[1])))
        return out

    obstacles = set(to_cells(observation.get("obstacles")))
    resources = to_cells(observation.get("resources"))
    rcount = observation.get("remaining_resource_count", None)
    have_res = bool(resources) or (rcount is not None and int(rcount) > 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mindist_to_list(x, y, lst):
        best = 10**9
        for a, b in lst:
            dx = x - a
            dy = y - b
            d = dx * dx + dy * dy
            if d < best:
                best = d
        return best

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if have_res:
            rd = mindist_to_list(nx, ny, resources) if resources else 0
            od = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            cell_bonus = 3 if (nx, ny) in set(resources) else 0
            score = cell_bonus * 10 - rd + 0.05 * od
        else:
            od = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            score = -od
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]