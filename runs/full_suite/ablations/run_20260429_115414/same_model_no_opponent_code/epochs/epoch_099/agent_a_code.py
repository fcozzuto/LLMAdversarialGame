def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            # nearest resource to us (tie: first in list)
            target = None
            d_to_res = 10**9
            for rx, ry in resources:
                d = manh(nx, ny, rx, ry)
                if d < d_to_res:
                    d_to_res = d
                    target = (rx, ry)
            tx, ty = target
            my_dist = d_to_res
            opp_dist = manh(ox, oy, tx, ty)
            dist_opp = manh(nx, ny, ox, oy)

            # maximize: closer to resource, farther from opponent; also try to beat opponent on the target
            val = (-my_dist * 10) + (dist_opp) + (6 if my_dist <= opp_dist else 0)
        else:
            # no resources: just move away from opponent toward center-ish
            dist_opp = manh(nx, ny, ox, oy)
            center_bias = -manh(nx, ny, (w - 1) // 2, (h - 1) // 2)
            val = dist_opp * 2 + center_bias

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]