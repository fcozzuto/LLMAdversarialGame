def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    rlist = [tuple(r) for r in resources]
    rset = set(rlist)

    # Target selection: maximize "reach advantage" (opponent farther than us).
    best_t = None
    best_key = None
    for rx, ry in rlist:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Prefer larger advantage, then closer to us, then lexicographic for determinism.
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Move scoring from immediate next position.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        immediate = 1 if (nx, ny) in rset else 0
        nd = abs(tx - nx) + abs(ty - ny)
        # Compare advantage after moving (estimate by distances).
        nsd = abs(tx - nx) + abs(ty - ny)
        nod = abs(tx - ox) + abs(ty - oy)
        adv = (nod - nsd)

        # Mild deterrent: don't step into squares adjacent to obstacles (but stay deterministic).
        adj_obs = 0
        if (nx, ny) not in obstacles:
            for ax, ay in [(nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1)]:
                if (ax, ay) in obstacles:
                    adj_obs += 1

        # Prefer immediate pickup, then higher advantage, then smaller distance to target.
        # Also keep tie-breaking deterministic via (nx, ny).
        score = (-(immediate), -(adv), nd, adj_obs, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]