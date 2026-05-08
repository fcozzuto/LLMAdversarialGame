def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_pts = []
    for p in unclaimed[:40]:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed_pts.append((x, y))

    resources = observation.get("resources") or []
    res_pts = set()
    for p in resources[:60]:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res_pts.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_v = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        cell = (nx, ny)

        if unclaimed_pts:
            d_un = min(md(cell, t) for t in unclaimed_pts)
        else:
            d_un = md(cell, (ox, oy))

        adj_opp = 1 if max(abs(nx - ox), abs(ny - oy)) == 1 else 0
        in_res = 1 if cell in res_pts else 0

        v = (-d_un) * 10 + adj_opp * 3 + in_res * 2
        if v > best_v or (v == best_v and (dx, dy) < best_move):
            best_v = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]