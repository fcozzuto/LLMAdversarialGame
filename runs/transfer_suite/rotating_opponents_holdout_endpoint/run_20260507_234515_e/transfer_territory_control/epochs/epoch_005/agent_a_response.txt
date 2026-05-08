def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    self_terr = set((tuple(p) for p in (observation.get("self_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2))
    opp_terr = set((tuple(p) for p in (observation.get("opponent_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2))
    unclaimed = set((tuple(p) for p in (observation.get("unclaimed_cells", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

    un_list = list(unclaimed)
    if not un_list:
        un_list = list(opp_terr) if opp_terr else list(self_terr)

    best = [0, 0]
    bestv = -10**18
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        v = 0.0
        if (nx, ny) in self_terr:
            v += 0.2
        elif (nx, ny) in opp_terr:
            v += 2.3
        elif (nx, ny) in unclaimed:
            v += 1.3
        else:
            v += 0.5

        nearest_un = 10**9
        for tx, ty in un_list:
            d = manh(nx, ny, tx, ty)
            if d < nearest_un:
                nearest_un = d
        v += -0.12 * nearest_un

        nearest_opp_terr = 10**9
        for tx, ty in opp_terr:
            d = manh(nx, ny, tx, ty)
            if d < nearest_opp_terr:
                nearest_opp_terr = d
        if opp_terr:
            v += -0.08 * nearest_opp_terr

        v += 0.06 * (manh(nx, ny, ox, oy) - manh(sx, sy, ox, oy))  # avoid getting too close

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best