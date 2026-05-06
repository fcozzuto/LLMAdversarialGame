def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        return [0, 0]

    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        our_dists = []
        best_adv = -10**9
        min_our = 10**9
        for rx, ry in resources:
            our_d = man((nx, ny), (rx, ry))
            opp_d = man((ox, oy), (rx, ry))
            adv = opp_d - our_d  # positive = we can reach sooner than opponent
            if adv > best_adv:
                best_adv = adv
            if our_d < min_our:
                min_our = our_d
            our_dists.append(our_d)
        # Also discourage moves that move us closer to opponent while we are not winning a resource
        opp_next = man((nx, ny), (ox, oy))
        key = (
            -best_adv * 10,         # maximize adv
            min_our,                # minimize our distance to some target
            opp_next,               # prefer staying away a bit (denier opponent)
            dx, dy                   # deterministic tie-break
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move