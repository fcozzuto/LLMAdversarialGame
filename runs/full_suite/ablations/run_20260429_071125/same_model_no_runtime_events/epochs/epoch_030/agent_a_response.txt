def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set()
    for p in observation["obstacles"]:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation["resources"]:
        if r is not None and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = (sx, sy)
    if resources:
        best_gain = -10**18
        for tx, ty in resources:
            own = man(sx, sy, tx, ty)
            opp = man(ox, oy, tx, ty)
            gain = opp - own  # prefer resources closer to us than opponent
            if gain > best_gain or (gain == best_gain and (own < man(sx, sy, target[0], target[1]))):
                best_gain = gain
                target = (tx, ty)
        if best_gain < 0:  # if opponent is closer to everything, fall back to nearest to us
            target = min(resources, key=lambda t: man(sx, sy, t[0], t[1]))

    resset = set(resources)
    best_move = [0, 0]
    best_score = -10**18
    tx, ty = target
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        own_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        on_res = 1 if (nx, ny) in resset else 0
        # prioritize picking resources, then improving our approach relative to opponent
        score = on_res * 100000 - own_d * 50 + (opp_d - own_d) * 5 - (abs(nx - ox) + abs(ny - oy)) * 0.5
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move