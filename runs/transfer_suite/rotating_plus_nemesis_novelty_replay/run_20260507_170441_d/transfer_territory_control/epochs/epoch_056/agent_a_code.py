def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh_count(tset, x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in tset:
                c += 1
        return c

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 10
        if (nx, ny) in opp_t:
            score -= 50
        score += 2 * neigh_count(self_t, nx, ny)
        score -= 3 * neigh_count(opp_t, nx, ny)

        # Prefer moves that reduce distance to opponent-unclaimed border when safe
        dist = abs(nx - ox) + abs(ny - oy)
        score += -0.3 * dist

        # Prefer staying or progressing deterministically
        if dx == 0 and dy == 0:
            score -= 0.1

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]