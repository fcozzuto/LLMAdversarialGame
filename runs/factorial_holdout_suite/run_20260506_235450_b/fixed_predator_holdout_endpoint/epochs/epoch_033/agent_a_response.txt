def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    late = int(observation.get("turns_remaining", 0) or 0) <= 3

    # Pick a target resource: early favor we-arrive-first; late favor shortest self path.
    best_r = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        if late:
            key = (-(ds), ds - do, do)  # minimize ds, then being farther behind opponent, then maximize do
        else:
            key = (ds - do, ds, do)  # minimize (we are ahead), then ds, then do
        if best_key is None or key < best_key:
            best_key = key
            best_r = [rx, ry]

    rx, ry = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_next = dist(nx, ny, rx, ry)
        do_cur = dist(ox, oy, rx, ry)
        advantage = do_cur - ds_next  # positive means we are closer than opponent at current turn
        val = advantage * 1000 - ds_next
        if late:
            # In late game, strongly prefer immediate collection and avoid moves that reduce distance too slowly.
            val += do_cur * 2
            if (nx, ny) == (rx, ry):
                val += 10**6
        else:
            # Early: if we're behind, still contest the closest catch-up resource; slight preference for staying central relative to target.
            val += (-(abs(nx - sx) + abs(ny - sy))) * 2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]