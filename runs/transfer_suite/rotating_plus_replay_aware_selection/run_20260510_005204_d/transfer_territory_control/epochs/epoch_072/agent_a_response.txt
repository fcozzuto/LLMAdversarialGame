def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        for p in list(unclaimed)[:]:
            resources.append(p)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbors4(x, y):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    best = (0, 0, None)  # (score, dist, target)
    candidates = []
    if resources:
        candidates.extend(resources)
    candidates.extend(list(unclaimed))
    if not candidates:
        candidates = [(sx, sy)]

    opp_pos = (ox, oy)
    for tx, ty in candidates[:min(40, len(candidates))]:
        if not inb(tx, ty):
            continue
        if (tx, ty) in self_terr:
            continue
        man_to_opp = abs(tx - opp_pos[0]) + abs(ty - opp_pos[1])
        man_to_self = abs(tx - sx) + abs(ty - sy)
        adjacent_self = 0
        adjacent_opp = 0
        for nx, ny in neighbors4(tx, ty):
            if (nx, ny) in self_terr:
                adjacent_self += 1
            if (nx, ny) in opp_terr:
                adjacent_opp += 1
        # Prefer edge/claim expansion that also pushes away from opponent.
        score = man_to_opp * 10 + adjacent_self * 6 - adjacent_opp * 4 - man_to_self * 2
        # If close to opponent territory, only take it when it also advances our adjacency.
        if adjacent_opp >= 2 and adjacent_self == 0:
            score -= 50
        # Prefer border cells slightly (vs edge-claimer).
        if tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1:
            score += 2
        dist = man_to_self
        if score > best[0] or (score == best[0] and dist < best[1]):
            best = (score, dist, (tx, ty))

    tx, ty = best[2] if best[2] is not None else (sx, sy)

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try diagonal first; if blocked, fall back to deterministic alternatives.
    steps = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for stx, sty in steps:
        nx, ny = sx + stx, sy + sty
        if inb(nx, ny):
            return [int(stx), int(sty)]
    return [0, 0]