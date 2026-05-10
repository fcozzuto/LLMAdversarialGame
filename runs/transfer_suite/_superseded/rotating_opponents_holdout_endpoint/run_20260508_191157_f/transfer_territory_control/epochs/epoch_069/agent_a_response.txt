def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_terr = []
    for t in observation.get("opponent_territory") or []:
        if t and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                opp_terr.append((x, y))

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    if opp_terr:
        targets = opp_terr
    else:
        targets = unclaimed
    if not targets:
        return [0, 0]

    ocx, ocy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    self_cnt = int(observation.get("self_territory_count", 0))
    opp_cnt = int(observation.get("opponent_territory_count", 0))
    turn_i = int(observation.get("turn_index", 0))
    leader_bias = 1.0
    if self_cnt >= opp_cnt:
        if turn_i % 10 == 0:
            leader_bias = 0.85
        else:
            leader_bias = 0.95
    else:
        if turn_i % 10 == 0:
            leader_bias = 1.15
        else:
            leader_bias = 1.05

    def best_target():
        best = None
        best_key = None
        for tx, ty in targets:
            md = abs(tx - sx) + abs(ty - sy)
            corner = abs(ocx - tx) + abs(ocy - ty)
            key = (md + 0.15 * corner, -corner)
            if best is None or key < best_key:
                best = (tx, ty)
                best_key = key
        return best

    tx, ty = best_target()

    def dist(x, y):
        return abs(tx - x) + abs(ty - y)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            d = dist(nx, ny)
            # tie-break deterministically: prefer toward opponent corner if we're behind
            corner_d = abs(ocx - nx) + abs(ocy - ny)
            score = d * leader_bias + 0.02 * corner_d
            candidates.append((score, d, corner_d, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda z: (z[0], z[1], z[2], z[3], z[4]))
    return [int(candidates[0][3]), int(candidates[0][4])]