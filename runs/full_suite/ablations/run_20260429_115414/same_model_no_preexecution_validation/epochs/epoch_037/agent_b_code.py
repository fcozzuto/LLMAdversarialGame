def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx = (w - 1 - sx)
        ty = (h - 1 - sy)
        if tx < 0: tx = 0
        elif tx > w - 1: tx = w - 1
        if ty < 0: ty = 0
        elif ty > h - 1: ty = h - 1
        resources = [(tx, ty)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        center = -(abs(rx - cx) + abs(ry - cy)) * 0.01
        key = (od - sd) * 1000 + center - sd * 1.0
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    rx, ry = best_r

    opp_bias = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Encourage moving closer; also slightly punish letting opponent be closer
        val = -self_d * 10.0 + (opp_d - self_d) * 2.0 + (-(abs(nx - cx) + abs(ny - cy))) * 0.01
        # If already in a race (opponent nearer), prioritize cutting distance most
        if opp_bias > 0:
            val += (-(self_d)) * 0.5
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]