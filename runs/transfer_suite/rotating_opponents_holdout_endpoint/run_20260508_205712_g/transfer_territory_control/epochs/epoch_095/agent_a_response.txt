def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def to_set(key):
        out = set()
        for c in observation.get(key) or []:
            if c and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")
    if not opp_t:
        opp_t = {(w - 1, h - 1)}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        cell = (nx, ny)
        if cell in opp_t:
            priority = 3
        elif cell in unclaimed:
            priority = 2
        elif cell in self_t:
            priority = 1
        else:
            priority = 0

        # Encourage moving near opponent territory while still choosing high-priority cells.
        dmin = None
        for ox, oy in opp_t:
            d = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            if dmin is None or d < dmin:
                dmin = d
                if dmin == 0:
                    break

        val = priority * 1000 - dmin
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
        elif val == best_val:
            # Deterministic tie-break: prefer staying, then left/up-ish.
            if (dx, dy) == (0, 0):
                best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]