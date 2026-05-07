def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def resource_key(rp, px, py):
        rx, ry = rp
        sd = cheb(px, py, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        row_push = (ry - oy)
        parity = ((rx + ry) & 1)
        return (adv, -sd, -abs(row_push), -parity)

    # If multiple resources, step to the best reachable adjacent cell
    best = None
    best_move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # If stepping onto a resource, prioritize heavily
            on_res = 0
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    on_res = 1
                    break
            if on_res:
                best_key = (10**9, 0, 0)
            else:
                # Evaluate best target from this next cell
                t = None
                for rp in resources:
                    k = resource_key(rp, nx, ny)
                    if t is None or k > t:
                        t = k
                # Also mildly prefer moving away from being blocked by obstacles
                block_pen = 0
                for ax in (-1, 0, 1):
                    for ay in (-1, 0, 1):
                        if ax == 0 and ay == 0:
                            continue
                        tx, ty = nx + ax, ny + ay
                        if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obs:
                            block_pen += 1
                best_key = (t[0], t[1], -block_pen)
            if best is None or best_key > best:
                best = best_key
                best_move = [dx, dy]

    return best_move