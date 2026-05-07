def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def turns(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))

    def best_for_pos(px, py):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = turns(px, py, rx, ry)
            do = turns(ox, oy, rx, ry)
            ahead = do - ds  # positive means we arrive earlier
            # Prefer earlier capture, then closer capture, then greater safety margin
            key = (ahead, -ds, -abs(rx - px) - abs(ry - py))
            if best is None or key > best[0]:
                best = (key, ds, do, rx, ry, ahead)
        return best

    best_move = (0, 0)
    best_key = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        b = best_for_pos(nx, ny)
        if b is None:
            continue
        (key, ds, do, rx, ry, ahead) = b
        # Extra push to pick a move that makes us strictly win at least one resource
        win_bonus = 2000000 if ahead > 0 else 0
        # Also reduce chances opponent can immediately take the same resource
        # by penalizing ds == do (tie race)
        tie_pen = 500000 if ahead == 0 else 0
        final_key = (win_bonus - tie_pen + key[0], key[1], key[2], -turns(nx, ny, ox, oy))
        if best_key is None or final_key > best_key:
            best_key = final_key
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]