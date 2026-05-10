def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs_set = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs_set.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic priority: center-ish then increasing x,y
    pref = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (0, -1): 3, (-1, 0): 4, (1, 1): 5, (-1, 1): 6, (1, -1): 7, (-1, -1): 8}
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs_set:
                return [int(dx), int(dy)]
        return [0, 0]

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_dist(pos):
        px, py = pos
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d = abs(rx - px) + abs(ry - py)
            if best is None or d < best:
                best = d
        return best if best is not None else 10**9

    # Choose which resource to contest: high priority if we can arrive earlier than opponent
    best_r = None
    best_r_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = manhattan((sx, sy), (rx, ry))
        do = manhattan((ox, oy), (rx, ry))
        # If ds is small and ds < do, good. If ds == do, favor breaking ties by position (deterministic).
        key = (-(ds < do), -(do - ds), -(-ds), (rx + ry) % 5, rx, ry)
        # Convert to a single total ordering by comparing tuple where "better" is lexicographically smaller for our construction
        if best_r is None or key < best_r_key:
            best_r = (rx, ry)
            best_r_key = key

    tx, ty = best_r

    def score_pos(pos):
        px, py = pos
        ds = manhattan((px, py), (tx, ty))
        # If we step onto another resource next turn, strongly reward (even if tx differs).
        nr = nearest_dist((px, py))
        opp_adv = manhattan((ox, oy), (tx, ty)) - manhattan((px, py), (tx, ty))
        return (ds, nr, -opp_adv)

    # Evaluate candidate moves
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obs_set:
            continue
        key = score_pos((nx, ny)) + (pref[(dx, dy)], nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]