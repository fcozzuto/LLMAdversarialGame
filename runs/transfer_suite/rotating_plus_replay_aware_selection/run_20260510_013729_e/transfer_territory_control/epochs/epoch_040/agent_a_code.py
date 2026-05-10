def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [sx, sy]) or [sx, sy]
    ox, oy = int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    blocks = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells") or set()
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = -10**18

    def adj8(x, y):
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocks:
            continue
        sc = 0
        if (nx, ny) in unclaimed:
            sc += 50
        if (nx, ny) in self_terr:
            sc -= 5
        if (nx, ny) in opp_terr:
            sc -= 100
        near_opp = any(c in opp_terr for c in adj8(nx, ny))
        near_self = any(c in self_terr for c in adj8(nx, ny))
        if near_opp:
            sc += 80
        if near_self:
            sc += 20
        # Prefer moving toward opponent-adjacent unclaimed when possible
        opp_dist = abs(nx - ox) + abs(ny - oy)
        sc += -opp_dist
        # If moving into unclaimed, add bonus for adjacency to opponent territory
        if (nx, ny) in unclaimed and near_opp:
            sc += 120
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]

    # Final fallback: deterministic move toward opponent, avoiding obstacles when possible
    for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocks:
            return [dx, dy]
    return [0, 0]