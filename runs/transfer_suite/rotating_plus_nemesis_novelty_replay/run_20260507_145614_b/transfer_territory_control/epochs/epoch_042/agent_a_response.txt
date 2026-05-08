def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((p[0], p[1]))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            oppT.add((p[0], p[1]))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    def pick_target(cands, prefer_opp_adj=False):
        best = None
        best_key = None
        for x, y in cands:
            d_self = abs(x - sx) + abs(y - sy)
            d_opp = abs(x - ox) + abs(y - oy)
            d_cent = abs(x - cx) + abs(y - cy)
            adj = 0
            if prefer_opp_adj:
                for nx, ny in neigh8(x, y):
                    if (nx, ny) in oppT:
                        adj += 1
            key = ((-adj if prefer_opp_adj else 0), d_self, d_cent, d_opp, x, y)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)
        return best

    target = pick_target(unclaimed, prefer_opp_adj=True)
    if target is None:
        if unclaimed:
            target = pick_target(unclaimed, prefer_opp_adj=False)
        elif resources:
            target = pick_target(resources, prefer_opp_adj=False)
        elif oppT:
            target = pick_target(list(oppT), prefer_opp_adj=False)
        else:
            return [0, 0]

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]