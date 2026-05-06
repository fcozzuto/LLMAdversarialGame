def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_dx, best_dy = 0, 0
    best_d = 10**9
    best_od = -1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if resources:
            md = 10**9
            for rx, ry in resources:
                dd = abs(rx - nx)
                dy2 = abs(ry - ny)
                if dy2 > dd:
                    dd = dy2
                if dd < md:
                    md = dd
                    if md == 0:
                        break
            od = abs(ox - nx)
            oy2 = abs(oy - ny)
            if oy2 > od:
                od = oy2
            if md < best_d or (md == best_d and od > best_od):
                best_d = md
                best_od = od
                best_dx, best_dy = dx, dy
        else:
            od = abs(ox - nx)
            oy2 = abs(oy - ny)
            if oy2 > od:
                od = oy2
            if od > best_od:
                best_od = od
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]