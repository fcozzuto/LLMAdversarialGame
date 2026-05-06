def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Opponent's most immediate target (deny/intercept bias)
    opp_target = None
    best_oppd = 10**18
    for rx, ry in resources:
        d = abs(ox - rx) + abs(oy - ry)
        if d < best_oppd:
            best_oppd = d
            opp_target = (rx, ry)

    def cell_value(nx, ny):
        # Attack: choose resource where we gain most distance advantage
        best_attack = -10**18
        best_selfd = 10**18
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)
            sc = (oppd - selfd) * 6 - selfd
            if sc > best_attack or (sc == best_attack and selfd < best_selfd):
                best_attack = sc
                best_selfd = selfd
        # Deny: reduce distance to opponent's nearest target
        rt = opp_target
        deny = 0
        if rt is not None:
            deny = -(abs(nx - rt[0]) + abs(ny - rt[1]))
        return best_attack + 3 * deny

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        v = cell_value(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]