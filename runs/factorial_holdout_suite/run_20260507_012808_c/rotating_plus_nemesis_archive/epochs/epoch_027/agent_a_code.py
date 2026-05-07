def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_action = (-(10**9), 10**9, 0)
    best_dxdy = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            nx, ny = sx, sy

        best_adv = -(10**9)
        best_dmy = 10**9
        best_tid = 0
        for i, (rx, ry) in enumerate(res):
            d_my = dist(nx, ny, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            adv = d_opp - d_my
            if adv > best_adv or (adv == best_adv and (d_my < best_dmy or (d_my == best_dmy and (rx + ry) < best_tid))):
                best_adv, best_dmy, best_tid = adv, d_my, rx + ry

        action_key = (best_adv, -best_dmy, -best_tid)
        if action_key > best_action:
            best_action = action_key
            best_dxdy = (nx - sx, ny - sy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]