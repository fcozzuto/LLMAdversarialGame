def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = {(x, y) for x, y in obstacles if inb(x, y)}
    my_set = {(x, y) for x, y in my_t if inb(x, y)}
    op_set = {(x, y) for x, y in op_t if inb(x, y)}
    un_set = {(x, y) for x, y in unclaimed if inb(x, y)}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bx, by = ax, ay

    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        # Heuristic: prefer taking opponent cells, then unclaimed; also move toward center,
        # but avoid leaving your territory too far from your expansion edge.
        if (nx, ny) in op_set:
            cell_bonus = 120
        elif (nx, ny) in un_set:
            cell_bonus = 60
        elif (nx, ny) in my_set:
            cell_bonus = 5
        else:
            cell_bonus = 15

        d_center = abs(nx - cx) + abs(ny - cy)

        # Expansion edge: if next to your territory, value increases slightly.
        adj_my = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                tx, ty = nx + ex, ny + ey
                if (tx, ty) in my_set:
                    adj_my = 1
                    break
            if adj_my:
                break

        # Minor bias to reduce distance from current target preference: center-first.
        score = cell_bonus - 2.0 * d_center + (8 if adj_my else 0)

        # Deterministic tie-break: higher score, then smaller dx, then smaller dy.
        key = (-score, dx, dy)
        if best is None or key < best:
            best = key
            bx, by = nx, ny

    if best is None:
        return [0, 0]
    return [bx - ax, by - ay]