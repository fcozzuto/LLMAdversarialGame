def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res_set = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res_set.add((x, y))
    if not res_set:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Focus: few closest resources to reduce brittleness
    res_list = list(res_set)
    res_list.sort(key=lambda p: cheb(sx, sy, p[0], p[1]))
    focus = res_list[:6] if len(res_list) > 6 else res_list

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in res_set:
            score += 1000

        my_min = 10**9
        opp_min = 10**9
        contested = 0
        for rx, ry in focus:
            d_my = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_my < my_min: my_min = d_my
            if d_opp < opp_min: opp_min = d_opp
            if d_my <= d_opp:
                contested += 1

        # Prefer moving closer, while preventing opponent advantage
        score += 30 / (1 + my_min)
        score += 8 * (1 / (1 + my_min) - 1 / (1 + opp_min))
        score += 3 * contested

        # Micro-avoid: if we could be stepping into obvious opponent reach while no immediate resource
        if (nx, ny) not in res_set:
            for adx, ady in dirs:
                tx, ty = nx + adx, ny + ady
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in res_set:
                    if cheb(ox, oy, tx, ty) <= cheb(ox, oy, nx, ny):
                        score -= 2

        if score > best_val:
            best_val = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]