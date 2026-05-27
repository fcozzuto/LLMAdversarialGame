def choose_move(observation):
    # Defensive extraction with defaults
    gw = observation.get("grid_width", 0)
    gh = observation.get("grid_height", 0)
    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    if not isinstance(me, (list, tuple)) or len(me) < 2:
        me = [0, 0]
    if not isinstance(opp, (list, tuple)) or len(opp) < 2:
        opp = [0, 0]

    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obs_set = set()
    if isinstance(obstacles, (list, tuple)):
        for o in obstacles:
            if isinstance(o, (list, tuple)) and len(o) >= 2:
                obs_set.add((int(o[0]), int(o[1])))

    res_pos = []
    if isinstance(resources, list):
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                res_pos.append((int(r[0]), int(r[1])))

    def within(nx, ny):
        if gw and gh:
            return 0 <= nx < gw and 0 <= ny < gh
        return True

    best = None
    best_d = 10**9
    for rx, ry in res_pos:
        d = abs(mx - rx) + abs(my - ry)
        if d < best_d and (rx, ry) not in obs_set:
            best_d = d
            best = (rx, ry)
    tx, ty = best if best is not None else (ox, oy)

    dx = 0
    dy = 0
    if tx > mx:
        dx = 1
    elif tx < mx:
        dx = -1
    if ty > my:
        dy = 1
    elif ty < my:
        dy = -1

    def blocked(nx, ny):
        return not within(nx, ny) or (nx, ny) in obs_set

    if blocked(mx + dx, my + dy):
        if dx != 0 and not blocked(mx + dx, my):
            dy = 0
        elif dy != 0 and not blocked(mx, my + dy):
            dx = 0
        else:
            dx, dy = 0, 0

    return [dx, dy]
