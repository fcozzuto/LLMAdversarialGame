def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed_list = observation.get("unclaimed_cells", []) or []
    unclaimed = set()
    for p in unclaimed_list:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    opp_terr_list = observation.get("opponent_territory", []) or []
    opp = set()
    for p in opp_terr_list:
        if p and len(p) >= 2:
            opp.add((int(p[0]), int(p[1])))

    self_terr_list = observation.get("self_territory", []) or []
    selft = set()
    for p in self_terr_list:
        if p and len(p) >= 2:
            selft.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_sc = -10**18

    ox, oy = observation.get("opponent_position", [sx, sy])
    ox, oy = int(ox), int(oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        sc = 0
        if (nx, ny) in unclaimed:
            sc += 100000
        if (nx, ny) in opp:
            sc += 200000
        if (nx, ny) in selft:
            sc += 5000

        # prefer being closer to nearest target, deterministically
        if unclaimed:
            mind = None
            for tx, ty in unclaimed:
                d = dist(nx, ny, tx, ty)
                if mind is None or d < mind or (d == mind and (tx, ty) < best[:2]):
                    mind = d
            sc += (10000 - 200 * mind)
        else:
            sc += (20000 - 50 * dist(nx, ny, ox, oy)) if unclaimed == set() else 0

        # slight penalty for staying still
        if dx == 0 and dy == 0:
            sc -= 50

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        # fallback: try any valid move including diagonal; else stay
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    return best