def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    obs_set = {(p[0], p[1]) for p in obstacles}
    resources = observation["resources"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        dx = 0
        dy = 0
        for cand in ([0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]):
            nx, ny = sx + cand[0], sy + cand[1]
            if inb(nx, ny) and (nx, ny) not in obs_set:
                dx, dy = cand
                break
        return [dx, dy]

    # Choose best resource: prefer ones we can reach much sooner than opponent.
    best = None
    best_val = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        val = (ds - do, ds, -rx, -ry)  # minimize ds-do, then ds, deterministic tie-break
        if best_val is None or val < best_val:
            best_val = val
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic move ordering already fixed by list order.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        ns = dist((nx, ny), (tx, ty))
        no = dist((ox, oy), (tx, ty))
        score = (ns - no, ns, abs((nx + ny) - (tx + ty)), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves blocked, stay.
    return [int(best_move[0]), int(best_move[1])]