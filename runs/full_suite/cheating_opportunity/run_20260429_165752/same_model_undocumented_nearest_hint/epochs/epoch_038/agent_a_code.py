def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obs:
            continue
        if (nx, ny) in res:
            return [dx, dy]
        if res:
            d = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        else:
            d = cheb(nx, ny, ox, oy)
        # Prefer approaching resources; slight bias to move away from opponent if no resources.
        opp_d = cheb(nx, ny, ox, oy)
        val = d * 1000 - (opp_d if not res else opp_d // 4)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]