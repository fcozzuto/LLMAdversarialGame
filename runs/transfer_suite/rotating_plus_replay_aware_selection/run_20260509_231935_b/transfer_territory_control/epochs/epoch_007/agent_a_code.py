def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = observation.get("obstacles", []) or []
    obs_set = {tuple(p) for p in obstacles}

    self_set = {tuple(p) for p in (observation.get("self_territory", []) or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory", []) or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells", []) or [])}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    def count_adj_to(sset, x, y):
        c = 0
        for dx, dy in neigh4:
            if (x + dx, y + dy) in sset:
                c += 1
        return c

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        if (nx, ny) in un_set:
            score += 6.0
            score += 0.1 * min(nx, ny, w - 1 - nx, h - 1 - ny)
        if (nx, ny) in opp_set:
            score += 10.0

        adj_self = count_adj_to(self_set, nx, ny)
        adj_un = count_adj_to(un_set, nx, ny)
        adj_opp = count_adj_to(opp_set, nx, ny)

        score += 1.8 * adj_self
        score += 1.2 * adj_un
        score -= 0.8 * adj_opp

        # deterministic "front push": prefer reducing distance to closest unclaimed when no direct hit
        if (nx, ny) not in un_set and un_set:
            best_d = 10**9
            for ux, uy in un_set:
                d = man(nx, ny, ux, uy)
                if d < best_d:
                    best_d = d
                    if best_d == 0:
                        break
            score += 2.0 / (1 + best_d)

        # mild penalty for staying boxed off by obstacles
        blocked = 0
        for tx, ty in neigh4:
            if not inb(nx + tx, ny + ty):
                blocked += 1
        score -= 0.15 * blocked

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]