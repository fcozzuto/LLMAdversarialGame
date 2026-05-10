def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    best = (-10**18, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        d_center = abs(nx - cx) + abs(ny - cy)
        d_self = abs(nx - sx) + abs(ny - sy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        adj_op = 0
        adj_me = 0
        for ax, ay in neigh8(nx, ny):
            if (ax, ay) in op_terr:
                adj_op += 1
            if (ax, ay) in my_terr:
                adj_me += 1

        if (nx, ny) in op_terr:
            score = 240 - 1.2 * d_center + 0.4 * d_opp - 0.08 * d_self + 25 * adj_me - 20 * adj_op
        elif (nx, ny) in unclaimed:
            score = 165 - 1.7 * d_center + 1.1 * d_opp - 0.06 * d_self + 18 * adj_me - 45 * adj_op
        elif (nx, ny) in my_terr:
            score = 25 - 1.0 * d_center + 0.2 * d_opp - 0.03 * d_self + 10 * adj_me - 10 * adj_op
        else:
            score = -1000000

        if score > best[0]:
            best = (score, dx, dy)

    if best[0] <= -10**17:
        return [0, 0]
    return [int(best[1]), int(best[2])]