def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    x0, y0 = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def cheb(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) >= abs(a[1] - b[1]) else abs(a[1] - b[1])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        best_t = None
        best_s = -10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obstacles:
                continue
            sd = cheb((x0, y0), (rx, ry))
            od = cheb((ox, oy), (rx, ry))
            s = (od - sd) * 10 - sd
            if s > best_s:
                best_s = s
                best_t = (rx, ry)
        if best_t is None:
            best_t = (x0, y0)
    else:
        best_t = (w // 2, h // 2)

    tx, ty = best_t
    cur_d = cheb((x0, y0), (tx, ty))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x0 + dx, y0 + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb((nx, ny), (tx, ty))
        adv_after = cheb((ox, oy), (tx, ty)) - nd
        adv_before = cheb((ox, oy), (tx, ty)) - cur_d
        val = -nd + (adv_after - adv_before) * 5
        if cheb((nx, ny), (ox, oy)) == 1:
            val -= 2
        if nd < cur_d and val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]