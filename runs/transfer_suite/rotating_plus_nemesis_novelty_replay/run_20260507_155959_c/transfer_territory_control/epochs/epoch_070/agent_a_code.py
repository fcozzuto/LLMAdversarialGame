def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    front_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

    def adj_to_self(x, y):
        for dx, dy in neigh8:
            if (x + dx, y + dy) in self_t:
                return True
        return False

    def adj_to_opp(x, y):
        for dx, dy in neigh8:
            if (x + dx, y + dy) in opp_t:
                return True
        return False

    moves = [(0, 0)]
    for dx, dy in front_dirs:
        moves.append((dx, dy))
    # deterministic tie-break order: as appended above

    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        score = 0
        if (nx, ny) in opp_t:
            score += 10 + (1 if adj_to_self(nx, ny) else 0) + (1 if adj_to_opp(nx, ny) else 0)
        elif (nx, ny) in self_t:
            score += 2
        elif (nx, ny) in unclaimed:
            score += 6
            if adj_to_self(nx, ny):
                score += 4
            if adj_to_opp(nx, ny):
                score += 2
            # slight preference for closer to center unclaimed to expand steadily
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score -= 0.01 * (abs(nx - cx) + abs(ny - cy))
        else:
            score -= 1

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best