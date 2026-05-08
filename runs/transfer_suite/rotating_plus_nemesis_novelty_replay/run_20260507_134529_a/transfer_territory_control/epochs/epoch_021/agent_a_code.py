def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur = (sx, sy)
    opp_list = list(opp_terr) if opp_terr else [(ox, oy)]
    opp_set = opp_terr
    best = None
    bestv = -10**18

    # Precompute for small, deterministic evaluation
    opp_min_from_cur = min(man(cur, p) for p in opp_list) if opp_list else 10**9
    unclaimed_list = list(unclaimed) if unclaimed else []

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        n = (nx, ny)

        cellv = 0
        if n in opp_set:
            cellv += 2000  # direct flip target
        elif n in unclaimed:
            cellv += 200
        elif n in self_terr:
            cellv += 40
        else:
            cellv += 0

        # Avoid opponent sweep proximity unless flipping
        oppd = min(man(n, p) for p in opp_list) if opp_list else 10**9
        # Encourage approaching opponent only when on/near their territory
        if n in opp_set or (oppd <= 2):
            cellv += (8 - oppd) * 25
        else:
            cellv -= max(0, 6 - oppd) * 30

        # If no good attacks, expand toward safe unclaimed on our side away from opponent
        if not unclaimed_list:
            cellv += (opp_min_from_cur - oppd) * 5
        else:
            # choose nearest unclaimed among a small deterministic subset
            # (sort-free: just sample first few by stable iteration order)
            subset = unclaimed_list[:12]
            tdmin = min(man(n, t) for t in subset) if subset else 10**9
            # Prefer reducing distance to unclaimed while keeping distance from opponent
            cellv += (120 - tdmin * 10)
            cellv += (oppd * 3)

        # Mild tie-break: keep movement compact/deterministic bias toward dx,dy ordering already set
        cellv -= (abs(dx) + abs(dy)) * 3
        if cellv > bestv:
            bestv = cellv
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]