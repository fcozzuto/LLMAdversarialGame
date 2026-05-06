def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    # No resources: drift to midline (intercepts future spawns deterministically)
    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (dist(nx, ny, tx, ty), dist(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    cx, cy = (gw - 1) / 2.0, (gh - 1) / 2.0
    best_move = None
    best_key = None

    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # For each move, choose the resource where we gain the most over opponent
        best_adv = None
        best_selfd = None
        best_cent = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # positive means we can arrive sooner (or equal if <=0 handled by tie-breaks)
            # Prefer larger advantage; then closer self; then closer to center (helps avoid dead-ends)
            cent = abs(rx - cx) + abs(ry - cy)
            key = (adv, -sd, -cent)
            if best_adv is None or key > best_adv:
                best_adv = key
                best_selfd = sd
                best_cent = cent
        # Also discourage moves that give opponent very small distance improvement by keeping us away
        # from the opponent unless it also improves advantage (captured mostly by adv)
        opp_to_next = dist(nx, ny, ox, oy)
        global_key = (best_adv[0], best_adv[1], -best_cent, opp_to_next, dx, dy)
        if best_key is None or global_key > best_key:
            best_key = global_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]