def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick best resource: maximize advantage (opp_dist - self_dist), tie-break by smaller self_dist.
    best_r = None
    best_adv = None
    best_sd = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if best_r is None or adv > best_adv or (adv == best_adv and ds < best_sd):
            best_r = (rx, ry)
            best_adv = adv
            best_sd = ds

    rx, ry = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Evaluate each neighbor by resulting advantage to the chosen target, with obstacle avoidance.
    best_m = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep in place; treat as invalid move
        ns = cheb(nx, ny, rx, ry)
        no = cheb(ox, oy, rx, ry)
        val = (no - ns, -ns)  # primary: maximize advantage, secondary: smaller distance
        if best_val is None or val > best_val:
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]