def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def to_xy(p):
        if not p:
            return (0, 0)
        return (int(float(p[0])), int(float(p[1])))

    sx, sy = to_xy(observation.get("self_position"))
    px, py = to_xy(observation.get("opponent_position"))

    def add_cells(key):
        out = set()
        for t in observation.get(key) or []:
            try:
                out.add((int(float(t[0])), int(float(t[1]))))
            except Exception:
                pass
        return out

    obstacles = add_cells("obstacles")
    unclaimed = add_cells("unclaimed_cells")
    self_terr = add_cells("self_territory")
    opp_terr = add_cells("opponent_territory")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Decide whether to expand or counterclaim.
    self_cnt = int(observation.get("self_territory_count", len(self_terr)) or len(self_terr))
    opp_cnt = int(observation.get("opponent_territory_count", len(opp_terr)) or len(opp_terr))
    attack = (opp_cnt >= self_cnt)

    target_set = opp_terr if attack else unclaimed
    fallback_set = unclaimed if attack else opp_terr

    if not target_set:
        target_set = fallback_set
    if not target_set:
        return [0, 0]

    # Greedy nearest target.
    tx, ty = None, None
    best_td = 10**18
    for x, y in target_set:
        if (x, y) in obstacles:
            continue
        d = dist2(sx, sy, x, y)
        if d < best_td:
            best_td = d
            tx, ty = x, y

    # Evaluate immediate moves.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = 0
        if (nx, ny) in unclaimed:
            cell += 12
        if (nx, ny) in opp_terr:
            cell += 20
        if (nx, ny) in self_terr:
            cell += 2

        dtar = dist2(nx, ny, tx, ty)
        # Prefer reducing distance to target and generally away from opponent.
        opp_d = dist2(nx, ny, px, py)
        score = cell * 10 - dtar + (1 if attack else 0) * (opp_d * 0.02)

        if (dx, dy) == (0, 0):
            score -= 1  # discourage wasting turns
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move