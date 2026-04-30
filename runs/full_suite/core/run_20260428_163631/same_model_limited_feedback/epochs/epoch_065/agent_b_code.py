def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obst = {(p[0], p[1]) for p in obstacles}
    res = [(p[0], p[1]) for p in resources] if resources else []
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def kdist(a, b, c, d):
        dx, dy = abs(a - c), abs(b - d)
        return dx if dx > dy else dy

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    best = None
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        if not res:
            min_res = 0
            best_diff = 0
        else:
            min_res = 10**9
            best_diff = -10**9
            for rx, ry in res:
                sd = kdist(nx, ny, rx, ry)
                od = kdist(ox, oy, rx, ry)
                if sd < min_res:
                    min_res = sd
                diff = od - sd
                if diff > best_diff:
                    best_diff = diff

        on_res = 1 if (nx, ny) in obst else 0
        on_res = 1 if (nx, ny) in set(res) else 0

        nf = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in obst:
                nf += 1

        opp_d = kdist(nx, ny, ox, oy)
        val = (1000 if on_res else 0) + 5 * best_diff - 2.2 * min_res + 0.8 * nf - 0.15 * opp_d

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]