def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(a), int(b)) for a, b in obstacles)

    resources = observation.get("resources", []) or []
    res_list = [(int(r[0]), int(r[1])) for r in resources]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = None  # (primary, secondary, tx, ty, dx, dy)
    if (x, y) in obs_set:
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    if (x, y) in res_list:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        if res_list:
            md = 10**9
            tx, ty = nx, ny
            for rx, ry in res_list:
                d = cheb(nx, ny, rx, ry)
                if d < md:
                    md = d
                    tx, ty = rx, ry
            # Prefer smaller resource distance; then prefer being farther from opponent
            od = cheb(nx, ny, ox, oy)
            cand = (md, -od, tx, ty, dx, dy)
        else:
            # No resources: keep away from opponent deterministically
            od = cheb(nx, ny, ox, oy)
            cand = (-od, 0, 0, 0, dx, dy)

        if best is None or cand < best:
            best = cand

    return [best[4], best[5]] if best is not None else [0, 0]