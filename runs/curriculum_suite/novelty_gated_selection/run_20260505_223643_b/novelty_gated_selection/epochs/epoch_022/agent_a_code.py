def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    favorable = []
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if ds <= do:
            favorable.append((ds, do, rx, ry))
    if favorable:
        target = min(favorable, key=lambda t: (t[0], t[2] + t[3]))
        tx, ty = target[2], target[3]
        flee = False
    else:
        # No resource we can secure first: run toward our nearest and away from opponent pressure.
        rx, ry = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
        tx, ty = rx, ry
        flee = True

    best = (None, None)  # (score, move)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_res = min(man(nx, ny, r[0], r[1]) for r in resources)
        d_to_tx = man(nx, ny, tx, ty)
        opp_near = min(man(ox, oy, r[0], r[1]) for r in resources)
        our_adv = opp_near - d_to_res  # higher is better
        if flee:
            score = (our_adv, d_to_tx, man(nx, ny, ox, oy))  # prefer staying farther from opponent
        else:
            score = (our_adv, -d_to_tx, -man(nx, ny, ox, oy))  # prefer tightening on target, not running
        if best[0] is None or score > best[0]:
            best = (score, [dx, dy])

    if best[1] is not None:
        return best[1]

    # If all moves blocked, stay.
    return [0, 0]