def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def is_free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    def adj_count(x, y, s):
        c = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in s:
                c += 1
        return c

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        score = 0
        if (nx, ny) in opp_t:
            score += 30 + 2 * adj_count(nx, ny, self_t)  # counter-claim
            score -= 2 * adj_count(nx, ny, opp_t)       # avoid deep inside opponent mass
        elif (nx, ny) in unclaimed:
            score += 18
            score += 5 * adj_count(nx, ny, self_t)      # frontier expansion
            score -= 6 * adj_count(nx, ny, opp_t)       # avoid easy counter-claim targets
            # prefer moving away from opponent slightly unless we're flipping
            score -= 2 * (max(abs(nx - ox), abs(ny - oy)) - max(abs(sx - ox), abs(sy - oy)))
        else:
            # moving within own territory or other non-claim cells: keep flexible but avoid stagnation
            score += 6 if (nx, ny) in self_t else 0
            score += 2 * adj_count(nx, ny, self_t)

        # small bias toward increasing distance from obstacles via center preference
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        score -= 0.1 * (abs(nx - cx) + abs(ny - cy))

        if score > best[1]:
            best = ([dx, dy], score)

    return best[0] if best[0] is not None else [0, 0]