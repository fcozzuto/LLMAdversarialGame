def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                unclaimed.add((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(a, b, c, d): return abs(a - c) + abs(b - d)

    # Targets: unclaimed frontier adjacent to our territory, else nearby unclaimed, else stay.
    frontier = []
    for x, y in unclaimed:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in self_terr:
                        frontier.append((x, y))
                        dx = dy = 2
                        break
            else:
                continue
            break
    targets = frontier if frontier else list(unclaimed)
    if not targets:
        return [0, 0]

    # Deterministic tie-break: fixed dir order.
    best = None
    best_score = -10**18
    txs = targets[:64]  # cap for speed, deterministic order from iteration
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep in place on invalid
        # Immediate landing value
        landing = 0
        if (nx, ny) in unclaimed:
            landing += 80
        if (nx, ny) in opp_terr:
            landing += 120
        if (nx, ny) in self_terr:
            landing -= 5

        # Approach value: go to nearest target, but slightly prefer targets away from opponent (deny sweep)
        mind = 10**9
        for tx, ty in txs:
            d = manh(nx, ny, tx, ty)
            if d < mind:
                mind = d
        deny = 0
        if targets:
            # prefer increasing distance to opponent if we can’t capture immediately
            deny = 0.1 * manh(nx, ny, ox, oy)

        score = landing - (mind * 10) + deny
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]