def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    def adj_to_opp(x, y):
        for dx, dy in neigh8:
            if (x + dx, y + dy) in opp_t:
                return True
        return False

    def manh(a, b, c, d): return abs(a - c) + abs(b - d)

    # Prefer immediate steal/claim, otherwise advance toward opponent-controlled frontier.
    best = (0, 0, -10**9)  # dx, dy, score
    for dx, dy in [(0, 0)] + neigh8:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        score = 0
        if (nx, ny) in opp_t:
            score += 120  # direct counter-claim
        elif (nx, ny) in unclaimed and (nx, ny) not in self_t and (nx, ny) not in opp_t:
            score += 70  # new claim
        elif (nx, ny) in self_t:
            score += 5   # maintain

        # Frontier pressure: moving adjacent to opponent territory is valuable even if not stealing immediately.
        if adj_to_opp(nx, ny):
            score += 35

        # Advance: bias toward reducing distance to opponent while staying near our frontier.
        score += -2 * manh(nx, ny, ox, oy)

        # Slight bias away from obstacles to avoid getting stuck.
        for adx, ady in neigh8:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in obstacles:
                score -= 6

        # Deterministic tie-break: prefer moves closer to diagonals then straight then stay.
        tie = (abs(dx) + abs(dy), -dx, -dy)
        if score > best[2] or (score == best[2] and tie > (abs(best[0]) + abs(best[1]), -best[0], -best[1])):
            best = (dx, dy, score)

    return [int(best[0]), int(best[1])]