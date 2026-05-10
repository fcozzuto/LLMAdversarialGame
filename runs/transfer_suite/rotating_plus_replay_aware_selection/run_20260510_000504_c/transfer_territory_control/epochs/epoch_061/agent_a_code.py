def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = list(map(tuple, observation.get("resources") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_sc = -10**18

    if resources:
        targets = resources
    elif unclaimed:
        targets = unclaimed
    elif opp_terr:
        targets = [sorted(opp_terr)[0]]
    else:
        targets = [(w - 1, h - 1)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if dx == 0 and dy == 0:
            pass
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in opp_terr:
            sc += 50
        if (nx, ny) in self_terr:
            sc += 10

        dmin = 10**9
        for tx, ty in targets:
            dmin = min(dmin, man(nx, ny, tx, ty))
        sc += 100 - dmin * 3

        if resources and dmin == 0:
            sc += 200

        do = man(nx, ny, ox, oy)
        sc -= do

        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best