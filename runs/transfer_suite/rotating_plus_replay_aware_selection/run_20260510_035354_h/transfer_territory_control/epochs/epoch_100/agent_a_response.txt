def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ax, ay, ox, oy = int(ax), int(ay), int(ox), int(oy)

    def toset(lst):
        s = set()
        if not lst:
            return s
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    myt = toset(observation.get("self_territory"))
    opt = toset(observation.get("opponent_territory"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist_m(a, b, c, d): return abs(a - c) + abs(b - d)

    def adj_to_me(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in myt:
                    return True
        return False

    # If surrounded/blocked, head toward best reachable unclaimed.
    best_target = None
    best_key = None
    for tx, ty in unclaimed:
        if (tx, ty) in obstacles:
            continue
        d_me = dist_m(ax, ay, tx, ty)
        d_op = dist_m(ox, oy, tx, ty)
        # Prefer expanding adjacent to our territory; otherwise prefer closeness and being farther from opponent.
        adj_bonus = -2 if adj_to_me(tx, ty) else 0
        # Keep diagonal corridors by slight penalty if alignment is weak.
        align_pen = 0 if (tx == ax or ty == ay or abs(tx - ax) == abs(ty - ay)) else 0.3
        key = (d_me + align_pen - adj_bonus, -d_op, ty, tx)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)

    if best_target is None:
        # Fallback: chase any cell near unclaimed (or just move toward opponent-remote corner)
        tx, ty = (0, 7) if ax < w // 2 else (7, 0)
    else:
        tx, ty = best_target

    # One-step evaluation to avoid stepping into obstacles while still moving toward target.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moving closer to target and being farther from opponent.
        d_t = dist_m(nx, ny, tx, ty)
        d_o = dist_m(nx, ny, ox, oy)
        is_unclaimed = (nx, ny) in unclaimed
        is_adj = adj_to_me(nx, ny)
        key = (d_t, -d_o, 0 if is_unclaimed else 1, -1 if is_adj else 0, dy, dx)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]