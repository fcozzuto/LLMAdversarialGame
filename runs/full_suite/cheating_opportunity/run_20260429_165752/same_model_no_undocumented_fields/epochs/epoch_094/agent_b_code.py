def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # Value: get to a resource while denying opponent; prioritize landing on a resource.
            val = 0
            if (nx, ny) in set(resources):
                val += 10**9
            # Choose best resource for this move (min my distance, then max opponent distance).
            my_best = 10**9
            opp_for_my_best = -1
            for rx, ry in resources:
                md = manh(nx, ny, rx, ry)
                od = manh(ox, oy, rx, ry)
                if md < my_best or (md == my_best and od > opp_for_my_best):
                    my_best = md
                    opp_for_my_best = od
            val += (opp_for_my_best - my_best) * 1000
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        # No resources: maximize distance from opponent; otherwise drift toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = manh(nx, ny, ox, oy) * 1000 - (abs(nx - cx) + abs(ny - cy))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]