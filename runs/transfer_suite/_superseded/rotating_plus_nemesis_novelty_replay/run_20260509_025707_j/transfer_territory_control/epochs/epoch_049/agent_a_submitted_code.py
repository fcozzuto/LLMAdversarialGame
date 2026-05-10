def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    unclaimed = observation.get("unclaimed_cells") or []
    res = observation.get("resources") or []
    cells = unclaimed if unclaimed else res
    myc = observation.get("self_territory_count", 0)
    opc = observation.get("opponent_territory_count", 0)
    behind = myc < opc

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    if cells:
        pts = [(p[0], p[1]) for p in cells if p and len(p) >= 2]
        pts = [t for t in pts if 0 <= t[0] < w and 0 <= t[1] < h and t not in obstacles]
        if pts:
            pts.sort(key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))
            best = pts[0]

    if best is None:
        # Fallback: keep distance from opponent, else drift toward center.
        target_x, target_y = (w // 2, h // 2)
        if man(sx, sy, ox, oy) < man(w // 2, h // 2, ox, oy):
            target_x, target_y = ox, oy
    else:
        target_x, target_y = best[0], best[1]

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    cur_dopp = man(sx, sy, ox, oy)

    best_move = moves[0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dtarget = man(nx, ny, target_x, target_y)
        dopp = man(nx, ny, ox, oy)
        if behind:
            val = -dtarget - 0.25 * max(0, (cur_dopp - dopp))
        else:
            val = -0.3 * dtarget + dopp
        if val > best_val or (val == best_val and (dx, dy) == best_move):
            best_val = val
            best_move = (dx, dy)

    if not (0 <= sx + best_move[0] < w and 0 <= sy + best_move[1] < h):
        return [0, 0]
    if (sx + best_move[0], sy + best_move[1]) in obstacles:
        # Last resort: try any valid move, deterministic.
        for dx, dy in moves:
            nx, ny = sx