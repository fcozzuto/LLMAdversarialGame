def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in moves[:-1]:
            nx, ny = x + dx, y + dy
            if safe(nx, ny):
                cnt += 1
        return cnt

    d_cur = abs(sx - ox) + abs(sy - oy)
    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_nxt = abs(nx - ox) + abs(ny - oy)
        fn = free_neighbors(nx, ny)
        ed = edge_dist(nx, ny)

        if evader:
            # Run away while avoiding trapping ourselves (prefer more mobility and not hugging walls).
            primary = d_nxt - d_cur
            key = (primary, fn, ed, -d_nxt, dx, dy)
        else:
            # Chase: reduce distance; if tie, keep mobility and avoid edges that can trap us behind obstacles.
            primary = d_cur - d_nxt
            key = (primary, fn, ed, -d_nxt, -dx, -dy)

        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move