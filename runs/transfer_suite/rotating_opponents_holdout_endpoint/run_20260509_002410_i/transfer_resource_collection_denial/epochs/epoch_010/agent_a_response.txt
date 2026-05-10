def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def safe_cell(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacle_set

    if not resources:
        return [0, 0]

    # Prefer resources where we are ahead (opponent farther than us); also avoid "distraction" near our path.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacle_set:
            continue
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        adv = od - sd
        # Tie-break: prefer smaller sd when adv equal; also slight preference to not move toward opponent.
        key = (adv, -sd, -manh(ox, oy, rx, ry), rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    # Choose best single-step move toward target, with local obstacle avoidance and opponent interference.
    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe_cell(nx, ny):
            continue
        # If landing on resource is great; otherwise reduce distance to target.
        d_to = manh(nx, ny, tx, ty)
        d_opp = manh(ox, oy, tx, ty)
        # Penalize stepping into positions that worsen our advantage immediately.
        sd_next = manh(nx, ny, tx, ty)
        adv_next = d_opp - sd_next
        # Slightly prefer moves that also increase distance from opponent to reduce interception.
        key = (adv_next, -d_to, -manh(nx, ny, ox, oy), -abs(tx - nx) - abs(ty - ny), dx, dy)
        if best_move is None or key > best_move[0]:
            best_move = (key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]