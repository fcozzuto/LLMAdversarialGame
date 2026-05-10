def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h
    obs_set = {(x, y) for x, y in obstacles if inb(x, y)}
    op_set = {(x, y) for x, y in op_t if inb(x, y)}
    un_set = {(x, y) for x, y in unclaimed if inb(x, y)}
    center = ((w - 1) / 2.0, (h - 1) / 2.0)

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny):
                        yield nx, ny

    frontier_un = set()
    for ux, uy in un_set:
        for nx, ny in neigh8(ux, uy):
            if (nx, ny) in op_set:
                frontier_un.add((ux, uy))
                break
    targets = list(frontier_un) if frontier_un else list(un_set)
    if not targets:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_s = -10**18
    best_d = [0, 0]

    cx, cy = center
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            if (nx, ny) not in inb(ax, ay):
                continue
        if not inb(nx, ny):
            continue
        min_dt = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < min_dt:
                min_dt = d
                if min_dt == 0:
                    break
        dc = (abs(nx - cx) + abs(ny - cy))
        # Prefer: closer to contested frontier/unclaimed, also drift toward center
        s = -min_dt * 10.0 - dc * 0.6
        # Add slight bias to keep pressure near opponent
        d_to_op = 10**9
        for px, py in op_t:
            d = abs(px - nx) + abs(py - ny)
            if d < d_to_op:
                d_to_op = d
        s += -d_to_op * 0.15
        # Deterministic tie-break: prefer smaller dx/dy lexicographically
        if s > best_s or (s == best_s and (dx, dy) < (best_d[0], best_d[1])):
            best_s = s
            best_d = [dx, dy]
    return best_d