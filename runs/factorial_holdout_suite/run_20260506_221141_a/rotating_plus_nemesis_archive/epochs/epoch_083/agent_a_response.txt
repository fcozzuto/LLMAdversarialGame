def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def eval_next(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        best = -10**9
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Prefer contested/lead resources; also prefer immediate pickups.
            s = (opp_d - self_d) * 100 - self_d
            if (nx, ny) == (rx, ry):
                s += 10**6
            if s > best:
                best = s
        return best if resources else -man(nx, ny, w - 1, h - 1)

    best_move = (0, 0)
    best_val = eval_next(sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            v = eval_next(nx, ny)
            if v > best_val:
                best_val, best_move = v, (dx, dy)
            elif v == best_val:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]