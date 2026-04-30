def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    res_map = {}
    resources = observation.get("resources") or []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                res_map[(x, y)] = res_map.get((x, y), 0) + 1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)
    res_list = list(res_map.keys())

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = dist_cheb(nx, ny, ox, oy)
        nearest_res = 10**9
        if res_list:
            for rx, ry in res_list:
                d = dist_cheb(nx, ny, rx, ry)
                if d < nearest_res:
                    nearest_res = d
        r_here = res_map.get((nx, ny), 0)
        w = 3 if len(res_list) >= 2 else 1
        score = r_here * (1000000 if r_here else 0) + (-w * d_opp) + (-2 * nearest_res if res_list else 0)
        cand = (score, dx, dy)
        if cand[0] > best[0] or (cand[0] == best[0] and (dx, dy) < (best[1], best[2])):
            best = cand

    return [int(best[1]), int(best[2])]